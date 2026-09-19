from pathlib import Path
from typing import Optional
import shutil
import tempfile

import pandas as pd

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ai.vision.predict import predict_image

from ai.root_cause.root_cause_engine import (
    analyze_root_cause,
)


# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="Industrial Defect Root-Cause AI",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

MODEL1_PATH = (
    BASE_DIR
    / "data"
    / "raw"
    / "model1"
    / "Model_1.csv"
)

MODEL2_PATH = (
    BASE_DIR
    / "data"
    / "raw"
    / "model2"
    / "Model_2.csv"
)


# ============================================================
# LOAD DATASETS
# ============================================================

def load_csv(path):

    try:

        dataframe = pd.read_csv(path)

        print(
            f"Loaded dataset: {path.name} "
            f"shape={dataframe.shape}"
        )

        return dataframe

    except Exception as error:

        print(
            f"Failed to load {path}: {error}"
        )

        return pd.DataFrame()


MODEL1_DATA = load_csv(
    MODEL1_PATH
)

MODEL2_DATA = load_csv(
    MODEL2_PATH
)


# ============================================================
# GLOBAL INSPECTION
# ============================================================

LATEST_INSPECTION = None


# ============================================================
# STATIONS
# ============================================================

STATIONS = {

    "Drilling": {
        "queue": "Drilling Queue Time",
        "utilization": "Drilling Utilization",
    },

    "Milling": {
        "queue": "Milling Queue Time",
        "utilization": "Milling Utilization",
    },

    "Assembly": {
        "queue": "Assembly Queue Time",
        "utilization": "Assembly Utilization",
    },

}


# ============================================================
# DEFECT PROCESS ASSOCIATION
# ============================================================
#
# These are investigation priors.
#
# They do NOT modify the real queue/utilization measurements.
#
# They are only used to calculate an additional
# defect-aware process relevance score.
#
# ============================================================

DEFECT_PROCESS_PRIORS = {

    "scratch": {
        "Drilling": 1.00,
        "Milling": 0.75,
        "Assembly": 0.50,
    },

    "bent": {
        "Drilling": 0.95,
        "Milling": 0.85,
        "Assembly": 0.45,
    },

    "color": {
        "Drilling": 0.45,
        "Milling": 0.70,
        "Assembly": 1.00,
    },

    "flip": {
        "Drilling": 0.65,
        "Milling": 0.95,
        "Assembly": 0.80,
    },

}


# ============================================================
# HELPERS
# ============================================================

def safe_float(value):

    try:
        return float(value)

    except Exception:
        return 0.0


# ============================================================
# PROCESS ANALYSIS
# ============================================================

def calculate_process_analysis():

    if MODEL2_DATA is None:
        return []

    if MODEL2_DATA.empty:
        return []


    station_values = {}

    max_queue = 0.0

    max_utilization = 0.0


    # --------------------------------------------------------
    # Collect raw measurements
    # --------------------------------------------------------

    for station, columns in STATIONS.items():

        queue_column = columns["queue"]

        utilization_column = columns[
            "utilization"
        ]


        if queue_column not in MODEL2_DATA.columns:

            print(
                f"Missing column: {queue_column}"
            )

            continue


        if utilization_column not in MODEL2_DATA.columns:

            print(
                f"Missing column: "
                f"{utilization_column}"
            )

            continue


        queue_value = safe_float(
            MODEL2_DATA[
                queue_column
            ].mean()
        )


        utilization_value = safe_float(
            MODEL2_DATA[
                utilization_column
            ].mean()
        )


        station_values[station] = {

            "queue_time": queue_value,

            "utilization": utilization_value,

        }


        max_queue = max(
            max_queue,
            queue_value,
        )


        max_utilization = max(
            max_utilization,
            utilization_value,
        )


    # --------------------------------------------------------
    # Calculate pressure
    # --------------------------------------------------------

    results = []


    for station, values in station_values.items():

        queue_pressure = (

            values["queue_time"]
            / max_queue

            if max_queue > 0
            else 0.0

        )


        utilization_pressure = (

            values["utilization"]
            / max_utilization

            if max_utilization > 0
            else 0.0

        )


        combined_pressure = (

            0.60 * queue_pressure
            +
            0.40 * utilization_pressure

        )


        results.append({

            "station": station,

            "queue_time": round(
                values["queue_time"],
                4,
            ),

            "utilization": round(
                values["utilization"],
                4,
            ),

            "queue_pressure": round(
                queue_pressure,
                4,
            ),

            "utilization_pressure": round(
                utilization_pressure,
                4,
            ),

            "pressure_score": round(
                combined_pressure,
                4,
            ),

            # Keep explicit base score
            # for defect-aware analysis.
            "base_pressure_score": round(
                combined_pressure,
                4,
            ),

        })


    # --------------------------------------------------------
    # Rank
    # --------------------------------------------------------

    results.sort(
        key=lambda item: item[
            "pressure_score"
        ],
        reverse=True,
    )


    for index, item in enumerate(
        results,
        start=1,
    ):

        item["rank"] = index


    return results


# ============================================================
# DEFECT-AWARE PROCESS ANALYSIS
# ============================================================

def calculate_defect_aware_process_analysis(
    process_analysis,
    defect_type,
):

    if not process_analysis:

        return []


    if not defect_type:

        return process_analysis


    priors = DEFECT_PROCESS_PRIORS.get(
        defect_type
    )


    # Unknown defect:
    # keep original production analysis.
    if not priors:

        output = []

        for item in process_analysis:

            copied = dict(item)

            copied[
                "defect_adjustment"
            ] = 1.0

            copied[
                "defect_aware_score"
            ] = copied[
                "base_pressure_score"
            ]

            output.append(copied)

        return output


    output = []


    for item in process_analysis:

        station = item[
            "station"
        ]


        prior = safe_float(
            priors.get(
                station,
                1.0,
            )
        )


        base_score = safe_float(
            item[
                "base_pressure_score"
            ]
        )


        defect_aware_score = (
            base_score * prior
        )


        copied = dict(item)


        copied[
            "defect_adjustment"
        ] = round(
            prior,
            4,
        )


        copied[
            "defect_aware_score"
        ] = round(
            defect_aware_score,
            4,
        )


        output.append(
            copied
        )


    output.sort(
        key=lambda item: item[
            "defect_aware_score"
        ],
        reverse=True,
    )


    for index, item in enumerate(
        output,
        start=1,
    ):

        item[
            "defect_aware_rank"
        ] = index


    return output


# ============================================================
# GET CURRENT DEFECT
# ============================================================

def get_current_defect_type():

    if not LATEST_INSPECTION:

        return None


    if not LATEST_INSPECTION.get(
        "is_defective",
        False,
    ):

        return None


    defect_type = (
        LATEST_INSPECTION.get(
            "defect_type"
        )
    )


    if defect_type:

        return defect_type

    return "visual anomaly"


# ============================================================
# INSPECTION PROCESS CONTEXT
# ============================================================

def get_inspection_process_context():

    # ALWAYS calculate the original
    # process measurements first.
    base_process = (
        calculate_process_analysis()
    )


    defect_type = (
        get_current_defect_type()
    )


    # No inspection yet.
    if LATEST_INSPECTION is None:

        return {

            "status": "awaiting_inspection",

            "defect_type": None,

            "process_analysis": base_process,

            "base_process_analysis": (
                base_process
            ),

            "defect_aware_process_analysis": [],

        }


    # Good image.
    if not LATEST_INSPECTION.get(
        "is_defective",
        False,
    ):

        return {

            "status": (
                "inspection_complete_no_anomaly"
            ),

            "defect_type": None,

            "process_analysis": base_process,

            "base_process_analysis": (
                base_process
            ),

            "defect_aware_process_analysis": [],

            "link_reason": (
                "No visual anomaly was "
                "detected. The production "
                "process measurements remain "
                "unchanged."
            ),

        }


    # Defective image.
    defect_aware = (
        calculate_defect_aware_process_analysis(
            base_process,
            defect_type,
        )
    )


    selected_process = (
        defect_aware[0]
        if defect_aware
        else None
    )


    return {

        "status": "inspection_linked",

        "defect_type": defect_type,

        # IMPORTANT:
        # Keep the original process analysis
        # here so existing frontend continues
        # working.
        "process_analysis": base_process,

        "base_process_analysis": (
            base_process
        ),

        # New defect-aware layer.
        "defect_aware_process_analysis": (
            defect_aware
        ),

        "selected_process": (
            selected_process
        ),

        "link_reason": (
            "The detected defect type is "
            "used to calculate an additional "
            "defect-aware process relevance "
            "score. Original queue and "
            "utilization measurements are "
            "not modified."
        ),

        "causality_note": (
            "This is an investigation "
            "hypothesis based on visual "
            "evidence, production data, and "
            "configured process priors. "
            "It does not prove causality."
        ),

    }


# ============================================================
# PRODUCTION SUMMARY
# ============================================================

def calculate_production_summary():

    if MODEL1_DATA.empty:

        return {

            "status": "unavailable"

        }


    total_parts = safe_float(
        MODEL1_DATA[
            "Total parts"
        ].sum()
    )


    average_parts_per_hour = safe_float(
        MODEL1_DATA[
            "Parts per hour"
        ].mean()
    )


    average_demand = safe_float(
        MODEL1_DATA[
            "Demand"
        ].mean()
    )


    return {

        "status": "success",

        "total_parts": round(
            total_parts,
            2,
        ),

        "average_parts_per_hour": round(
            average_parts_per_hour,
            2,
        ),

        "average_demand": round(
            average_demand,
            2,
        ),

    }


# ============================================================
# PRODUCTION IMPACT
# ============================================================

def calculate_production_impact():

    production = (
        calculate_production_summary()
    )


    if production.get(
        "status"
    ) != "success":

        return production


    total_parts = production[
        "total_parts"
    ]


    average_parts_per_hour = production[
        "average_parts_per_hour"
    ]


    # Demo assumptions.
    defect_rate = 0.05

    scrap_cost_per_part = 250

    rework_cost_per_part = 100

    downtime_cost_per_hour = 1500


    estimated_defective_parts = (
        total_parts
        * defect_rate
    )


    scrap_cost = (
        estimated_defective_parts
        * scrap_cost_per_part
    )


    rework_cost = (
        estimated_defective_parts
        * rework_cost_per_part
    )


    process = (
        calculate_process_analysis()
    )


    bottleneck = (
        process[0]
        if process
        else None
    )


    queue_time = (

        safe_float(
            bottleneck[
                "queue_time"
            ]
        )

        if bottleneck

        else 0.0

    )


    downtime_hours = (
        queue_time / 60.0
    )


    downtime_cost = (
        downtime_hours
        * downtime_cost_per_hour
    )


    total_impact = (
        scrap_cost
        +
        rework_cost
        +
        downtime_cost
    )


    return {

        "status": "success",

        "total_parts": round(
            total_parts,
            2,
        ),

        "average_parts_per_hour": round(
            average_parts_per_hour,
            2,
        ),

        "assumed_defect_rate": (
            defect_rate
        ),

        "estimated_defective_parts": round(
            estimated_defective_parts,
            2,
        ),

        "scrap_cost": round(
            scrap_cost,
            2,
        ),

        "rework_cost": round(
            rework_cost,
            2,
        ),

        "downtime_cost": round(
            downtime_cost,
            2,
        ),

        "estimated_total_impact": round(
            total_impact,
            2,
        ),

        "bottleneck_station": (
            bottleneck[
                "station"
            ]
            if bottleneck
            else None
        ),

        "assumptions": {

            "scrap_cost_per_part": (
                scrap_cost_per_part
            ),

            "rework_cost_per_part": (
                rework_cost_per_part
            ),

            "downtime_cost_per_hour": (
                downtime_cost_per_hour
            ),

        },

        "note": (
            "Economic values are configurable "
            "demo assumptions and are not actual "
            "factory losses."
        ),

    }


# ============================================================
# SIMULATION
# ============================================================

class SimulationRequest(BaseModel):

    throughput_change_percent: float = 0.0

    defect_reduction_percent: float = 0.0

    downtime_reduction_percent: float = 0.0


def run_simulation(
    payload: SimulationRequest
):

    production = (
        calculate_production_summary()
    )


    if production.get(
        "status"
    ) != "success":

        return production


    base_throughput = production[
        "average_parts_per_hour"
    ]


    base_defect_rate = 5.0


    simulated_throughput = (
        base_throughput
        *
        (
            1
            +
            payload.throughput_change_percent
            / 100
        )
    )


    simulated_defect_rate = (
        base_defect_rate
        *
        (
            1
            -
            payload.defect_reduction_percent
            / 100
        )
    )


    simulated_downtime = (
        100
        *
        (
            1
            -
            payload.downtime_reduction_percent
            / 100
        )
    )


    return {

        "status": "simulation_complete",

        "baseline": {

            "throughput": round(
                base_throughput,
                2,
            ),

            "defect_rate_percent": (
                base_defect_rate
            ),

            "downtime_index": 100,

        },

        "scenario": {

            "throughput": round(
                simulated_throughput,
                2,
            ),

            "defect_rate_percent": round(
                simulated_defect_rate,
                2,
            ),

            "downtime_index": round(
                simulated_downtime,
                2,
            ),

        },

        "changes": {

            "throughput_change_percent": (
                payload.throughput_change_percent
            ),

            "defect_reduction_percent": (
                payload.defect_reduction_percent
            ),

            "downtime_reduction_percent": (
                payload.downtime_reduction_percent
            ),

        },

    }


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {

        "name": (
            "Industrial Defect "
            "Root-Cause AI"
        ),

        "status": "running",

        "pipeline": (
            "Image → Defect → "
            "Process Evidence → "
            "Root Cause → Bottleneck → "
            "Production Impact → "
            "Economics → Simulation"
        ),

    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():

    return {

        "status": "healthy",

        "model1_loaded": (
            not MODEL1_DATA.empty
        ),

        "model2_loaded": (
            not MODEL2_DATA.empty
        ),

        "latest_inspection": (
            LATEST_INSPECTION is not None
        ),

    }


# ============================================================
# PROCESS
# ============================================================

@app.get("/process")
def process():

    return {

        "status": "success",

        "stations": (
            calculate_process_analysis()
        ),

    }


# ============================================================
# BOTTLENECK
# ============================================================

@app.get("/bottleneck")
def bottleneck():

    context = (
        get_inspection_process_context()
    )


    base_stations = (
        context.get(
            "base_process_analysis",
            [],
        )
    )


    defect_aware_stations = (
        context.get(
            "defect_aware_process_analysis",
            [],
        )
    )


    # Keep the ORIGINAL stations field
    # because your existing frontend uses it.
    return {

        "status": "success",

        "analysis_mode": (

            "defect_aware"

            if context.get(
                "defect_type"
            )

            else "production_only"

        ),

        "defect_type": (
            context.get(
                "defect_type"
            )
        ),

        # Existing frontend field.
        "stations": base_stations,

        # New field for future UI.
        "defect_aware_stations": (
            defect_aware_stations
        ),

        "top_process_candidate": (

            (
                defect_aware_stations[0]
                if defect_aware_stations
                else (
                    base_stations[0]
                    if base_stations
                    else None
                )
            )

        ),

        "inspection_context": context,

    }


# ============================================================
# PRODUCTION
# ============================================================

@app.get("/production")
def production():

    return {

        "status": "success",

        "production": (
            calculate_production_summary()
        ),

    }


# ============================================================
# IMPACT
# ============================================================

@app.get("/impact")
def impact():

    return {

        "status": "success",

        "impact": (
            calculate_production_impact()
        ),

    }


# ============================================================
# ROOT CAUSE
# ============================================================

@app.get("/root-cause")
def root_cause():

    defect_type = (
        get_current_defect_type()
    )


    if not defect_type:

        return {

            "status": "awaiting_inspection",

            "message": (
                "Upload a defective image "
                "to run defect-specific "
                "root-cause analysis."
            ),

        }


    try:

        result = (
            analyze_root_cause(
                defect_type
            )
        )


        return result


    except Exception as error:

        return {

            "status": "root_cause_error",

            "error": str(
                error
            ),

        }


# ============================================================
# SIMULATION
# ============================================================

@app.post("/simulation")
def simulation(
    payload: SimulationRequest
):

    return run_simulation(
        payload
    )


# ============================================================
# COMPLETE ANALYSIS
# ============================================================

@app.get("/analysis")
def analysis():

    inspection = (
        LATEST_INSPECTION
    )


    process_context = (
        get_inspection_process_context()
    )


    defect_type = (
        get_current_defect_type()
    )


    root_cause = None


    if defect_type:

        try:

            root_cause = (
                analyze_root_cause(
                    defect_type
                )
            )

        except Exception as error:

            root_cause = {

                "status": (
                    "root_cause_error"
                ),

                "error": str(
                    error
                ),

            }


    return {

        "status": "success",

        "inspection": inspection,

        "vision": inspection,

        "process": process_context,

        "root_cause": root_cause,

        "production": (
            calculate_production_summary()
        ),

        "economics": (
            calculate_production_impact()
        ),

        "simulation": {

            "status": "ready"

        },

    }


# ============================================================
# INSPECTION
# ============================================================

@app.post("/inspection")
async def inspection(
    file: UploadFile = File(...)
):

    global LATEST_INSPECTION


    if not file.filename:

        return {

            "status": "inspection_failed",

            "message": (
                "No image file selected."
            ),

        }


    extension = (
        Path(
            file.filename
        ).suffix.lower()
    )


    allowed_extensions = {

        ".jpg",
        ".jpeg",
        ".png",
        ".webp",

    }


    if extension not in allowed_extensions:

        return {

            "status": "inspection_failed",

            "message": (
                "Unsupported image format. "
                "Use JPG, JPEG, PNG, or WEBP."
            ),

        }


    temp_path = None


    try:

        # ----------------------------------------------------
        # SAVE UPLOADED IMAGE
        # ----------------------------------------------------

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=extension,
        ) as temp_file:

            temp_path = Path(
                temp_file.name
            )


            shutil.copyfileobj(
                file.file,
                temp_file,
            )


        # ----------------------------------------------------
        # RUN VISION MODEL
        # ----------------------------------------------------

        vision_result = (
            predict_image(
                temp_path
            )
        )


        is_defective = (
            vision_result.get(
                "is_defective",
                False,
            )
        )


        defect_type = (
            vision_result.get("defect_type")
            or ("visual anomaly" if is_defective else None)
        )


        # ----------------------------------------------------
        # STORE INSPECTION
        # ----------------------------------------------------

        LATEST_INSPECTION = {

            "filename": (
                file.filename
            ),

            "status": (
                vision_result.get(
                    "status"
                )
            ),

            "anomaly_score": (
                vision_result.get(
                    "anomaly_score"
                )
            ),

            "threshold": (
                vision_result.get(
                    "threshold"
                )
            ),

            "is_defective": (
                is_defective
            ),

            "defect_type": (
                defect_type
            ),

            "classification_confidence": (
                vision_result.get(
                    "classification_confidence"
                )
            ),

            "prototype_similarity": (
                vision_result.get(
                    "prototype_similarity"
                )
            ),

            "class_scores": (
                vision_result.get(
                    "class_scores"
                )
            ),

            "model": (
                vision_result.get(
                    "model"
                )
            ),

        }


        # ----------------------------------------------------
        # PROCESS CONTEXT
        # ----------------------------------------------------

        process_context = (
            get_inspection_process_context()
        )


        # ----------------------------------------------------
        # ROOT CAUSE
        # ----------------------------------------------------

        root_cause = None


        if (
            is_defective
            and defect_type
        ):

            try:

                root_cause = (
                    analyze_root_cause(
                        defect_type
                    )
                )

            except Exception as error:

                root_cause = {

                    "status": (
                        "root_cause_error"
                    ),

                    "error": str(
                        error
                    ),

                }


        # ----------------------------------------------------
        # COMPLETE RESPONSE
        # ----------------------------------------------------

        return {

            # IMPORTANT:
            # Frontend expects this.
            "status": (
                "inspection_complete"
            ),

            "message": (
                "Image inspection completed."
            ),

            # Original inspection object.
            "inspection": (
                LATEST_INSPECTION
            ),

            # Vision result.
            "vision": (
                vision_result
            ),

            # Process result.
            "process": (
                process_context
            ),

            # Root cause.
            "root_cause": (
                root_cause
            ),

            # Production.
            "production": (
                calculate_production_summary()
            ),

            # Economics.
            "economics": (
                calculate_production_impact()
            ),

        }


    except Exception as error:

        print(
            "Inspection error:",
            error,
        )


        return {

            "status": "inspection_failed",

            "message": str(
                error
            ),

        }


    finally:

        if temp_path:

            try:

                if temp_path.exists():

                    temp_path.unlink()

            except Exception:

                pass