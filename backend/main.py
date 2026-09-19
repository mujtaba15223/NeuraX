from pathlib import Path
import os

import pandas as pd
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from ai.vision.predict import predict_image
from ai.root_cause.root_cause_engine import (
    analyze_root_cause,
)


# ============================================================
# APP CONFIGURATION
# ============================================================

app = FastAPI(
    title="Industrial Defect Root-Cause AI",
    description=(
        "AI-powered industrial inspection and "
        "decision-support system"
    ),
    version="1.0.0",
)


FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN")


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ] + ([FRONTEND_ORIGIN] if FRONTEND_ORIGIN else []),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent


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


UPLOAD_DIR = (
    BASE_DIR
    / "data"
    / "processed"
    / "vision"
    / "uploads"
)


UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# ECONOMIC ASSUMPTIONS
# ============================================================

SCRAP_COST_PER_PART = 250
REWORK_COST_PER_PART = 100
DOWNTIME_COST_PER_HOUR = 1500

ASSUMED_DEFECT_RATE = 0.05


# ============================================================
# DATA LOADERS
# ============================================================

def load_model1():

    return pd.read_csv(
        MODEL1_PATH
    )


def load_model2():

    return pd.read_csv(
        MODEL2_PATH
    )


# ============================================================
# PROCESS ANALYSIS
# ============================================================

def calculate_process_analysis():

    df = load_model2()

    stations = {
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

    avg_queues = {
        station: float(
            df[data["queue"]].mean()
        )
        for station, data in stations.items()
    }

    avg_utilizations = {
        station: float(
            df[data["utilization"]].mean()
        )
        for station, data in stations.items()
    }

    max_queue = max(
        avg_queues.values()
    )

    max_utilization = max(
        avg_utilizations.values()
    )

    results = []

    for station, data in stations.items():

        avg_queue = avg_queues[
            station
        ]

        avg_utilization = (
            avg_utilizations[
                station
            ]
        )

        queue_pressure = (
            avg_queue / max_queue
            if max_queue > 0
            else 0
        )

        utilization_pressure = (
            avg_utilization
            / max_utilization
            if max_utilization > 0
            else 0
        )

        score = (
            0.60 * queue_pressure
            + 0.40 * utilization_pressure
        )

        results.append(
            {
                "station": station,

                "avg_queue": round(
                    avg_queue,
                    4,
                ),

                "utilization": round(
                    avg_utilization,
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

                "score": round(
                    score,
                    4,
                ),
            }
        )

    results.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return results


# ============================================================
# PRODUCTION IMPACT
# ============================================================

def calculate_production_impact():

    df = load_model1()

    total_parts = float(
        df["Total parts"].sum()
    )

    average_parts_per_hour = float(
        df["Parts per hour"].mean()
    )

    average_demand = float(
        df["Demand"].mean()
    )

    estimated_defective_parts = (
        total_parts
        * ASSUMED_DEFECT_RATE
    )

    scrap_cost = (
        estimated_defective_parts
        * SCRAP_COST_PER_PART
    )

    rework_cost = (
        estimated_defective_parts
        * REWORK_COST_PER_PART
    )

    bottleneck_station = "Assembly"

    average_waiting_time = float(
        df["Assembly Waiting Time"].mean()
    )

    downtime_cost = (
        average_waiting_time
        / 60
        * DOWNTIME_COST_PER_HOUR
    )

    total_estimated_impact = (
        scrap_cost
        + rework_cost
        + downtime_cost
    )

    return {
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

        "assumed_defect_rate": (
            ASSUMED_DEFECT_RATE
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

        "bottleneck_station": (
            bottleneck_station
        ),

        "average_waiting_time": round(
            average_waiting_time,
            2,
        ),

        "downtime_cost": round(
            downtime_cost,
            2,
        ),

        "total_estimated_impact": round(
            total_estimated_impact,
            2,
        ),

        "note": (
            "Economic values are configurable "
            "demonstration assumptions, not actual "
            "financial losses."
        ),
    }


# ============================================================
# ROOT CAUSE
# ============================================================

def calculate_root_cause(
    defect_type="scratch"
):

    return analyze_root_cause(
        defect_type=defect_type
    )


# ============================================================
# BASIC ROUTES
# ============================================================

@app.get("/")
def root():

    return {
        "name": (
            "Industrial Defect Root-Cause AI"
        ),

        "status": "online",

        "version": "1.0.0",
    }


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# ============================================================
# PROCESS
# ============================================================

@app.get("/process")
def process():

    analysis = (
        calculate_process_analysis()
    )

    return {
        "process_analysis": analysis,

        "top_process_candidate": (
            analysis[0]
        ),
    }


# ============================================================
# ROOT CAUSE
# ============================================================

@app.get("/root-cause")
def root_cause():

    return calculate_root_cause(
        defect_type="scratch"
    )


# ============================================================
# IMPACT
# ============================================================

@app.get("/impact")
def impact():

    return calculate_production_impact()


# ============================================================
# UNIFIED ANALYSIS
# ============================================================

@app.get("/analysis")
def analysis():

    process_analysis = (
        calculate_process_analysis()
    )

    root_cause = (
        calculate_root_cause(
            defect_type="scratch"
        )
    )

    production_impact = (
        calculate_production_impact()
    )

    return {
        "vision": {
            "status": "inspection_ready",
            "defect": "scratch",
        },

        "process": {
            "process_analysis": (
                process_analysis
            ),

            "top_process_candidate": (
                process_analysis[0]
            ),
        },

        "root_cause": root_cause,

        "production_impact": (
            production_impact
        ),
    }


# ============================================================
# REAL AI IMAGE INSPECTION
# ============================================================

@app.post("/inspection")
async def inspection(
    file: UploadFile = File(...)
):

    allowed_types = {
        "image/jpeg",
        "image/png",
        "image/webp",
    }

    if file.content_type not in allowed_types:

        return {
            "status": "error",

            "message": (
                "Please upload a JPG, PNG, "
                "or WEBP image."
            ),
        }

    image_data = await file.read()

    if not image_data:

        return {
            "status": "error",

            "message": (
                "Uploaded image is empty."
            ),
        }

    safe_filename = Path(
        file.filename or "inspection.png"
    ).name

    image_path = (
        UPLOAD_DIR
        / safe_filename
    )

    image_path.write_bytes(
        image_data
    )

    try:

        # ====================================================
        # STEP 1 — VISION INSPECTION
        # ====================================================

        vision_result = predict_image(
            image_path
        )

        # ====================================================
        # DEBUG — SHOW EXACT AI RESULT
        # ====================================================

        print()
        print("=" * 70)
        print("VISION RESULT FROM UPLOAD:")
        print(vision_result)
        print("=" * 70)
        print()

        # ====================================================
        # STEP 2 — DETERMINE DEFECT
        # ====================================================

        is_defective = bool(
            vision_result.get(
                "is_defective",
                False,
            )
        )

        detected_defect = (
            "scratch"
            if is_defective
            else "none"
        )

        # ====================================================
        # STEP 3 — ROOT CAUSE
        # ====================================================

        root_cause_result = None

        if is_defective:

            root_cause_result = (
                calculate_root_cause(
                    defect_type=detected_defect
                )
            )

        # ====================================================
        # STEP 4 — RETURN COMPLETE RESULT
        # ====================================================

        return {

            "status": vision_result.get(
                "status",
                "unknown",
            ),

            "filename": safe_filename,

            "content_type": (
                file.content_type
            ),

            "size_bytes": len(
                image_data
            ),

            "anomaly_score": (
                vision_result.get(
                    "anomaly_score",
                    0,
                )
            ),

            "threshold": (
                vision_result.get(
                    "threshold",
                    0,
                )
            ),

            "is_defective": (
                is_defective
            ),

            "model": (
                vision_result.get(
                    "model",
                    "unknown",
                )
            ),

            "defect_type": (
                detected_defect
            ),

            "root_cause": (
                root_cause_result
            ),
        }

    except Exception as error:

        print()
        print("=" * 70)
        print("VISION INSPECTION ERROR:")
        print(error)
        print("=" * 70)
        print()

        return {

            "status": "error",

            "message": (
                "Vision inspection failed."
            ),

            "details": str(error),
        }