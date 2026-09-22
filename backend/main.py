from pathlib import Path
from typing import Optional
import os
import shutil
import tempfile

import pandas as pd

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ai.vision.predict import predict_image

from ai.root_cause.root_cause_engine import (
    analyze_root_cause,
)
from backend.services.manufacturing_data import (
    discover_station_columns,
    export_headers,
    numeric_mean,
    numeric_sum,
    resolve_production_columns,
)

from simulation.production_simulation import ProductionParameters
from simulation.what_if import WhatIfSimulator
from simulation.scenarios import Scenario, list_scenarios


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

MODEL1_DATA_PATH = (
    BASE_DIR
    / "data"
    / "raw"
    / "model1"
    / "Model_1.csv"
)

MODEL2_DATA_PATH = (
    BASE_DIR
    / "data"
    / "raw"
    / "model2"
    / "Model_2.csv"
)

QUALITY_DATA_PATH = (
    BASE_DIR
    / "data"
    / "raw"
    / "new"
    / "product-quality-control.csv"
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
    MODEL1_DATA_PATH
)

MODEL2_DATA = load_csv(
    MODEL2_DATA_PATH
)

QUALITY_DATA = load_csv(
    QUALITY_DATA_PATH
)

# Compatibility alias for existing service code and response contracts.
MANUFACTURING_DATA = MODEL1_DATA


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


    production_columns = resolve_production_columns(
        MODEL2_DATA
    )

    machine_column = production_columns.get(
        "machine_id"
    )

    if machine_column:
        return calculate_oee_process_analysis(
            MODEL2_DATA,
            production_columns,
        )

    station_columns = discover_station_columns(
        MODEL2_DATA
    )

    station_values = {}

    max_queue = 0.0

    max_utilization = 0.0


    # --------------------------------------------------------
    # Collect raw measurements
    # --------------------------------------------------------

    for station, columns in station_columns.items():

        queue_value = numeric_mean(
            MODEL2_DATA,
            columns["queue"],
        )

        utilization_value = numeric_mean(
            MODEL2_DATA,
            columns["utilization"],
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

            # Compatibility aliases used by existing frontend pages.
            "avg_queue": round(values["queue_time"], 4),
            "score": round(combined_pressure, 4),

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


def calculate_oee_process_analysis(
    dataframe,
    columns,
):
    machine_column = columns.get("machine_id")
    planned_column = columns.get("planned_hours")
    actual_column = columns.get("actual_hours")
    availability_column = columns.get("availability")
    performance_column = columns.get("performance")
    quality_column = columns.get("quality")
    oee_column = columns.get("oee")
    units_column = columns.get("total_parts")
    defects_column = columns.get("defects")

    required = {
        "machine_id": machine_column,
        "planned_hours": planned_column,
        "actual_hours": actual_column,
        "availability": availability_column,
        "performance": performance_column,
        "quality": quality_column,
        "oee": oee_column,
        "units_produced": units_column,
        "defects": defects_column,
    }

    if any(value is None for value in required.values()):
        return []

    grouped = dataframe.groupby(machine_column, dropna=True)
    rows = []

    for machine, group in grouped:
        planned_hours = numeric_sum(group, planned_column)
        actual_hours = numeric_sum(group, actual_column)
        downtime_hours = max(0.0, planned_hours - actual_hours)
        units = numeric_sum(group, units_column)
        defects = numeric_sum(group, defects_column)

        rows.append({
            "station": str(machine),
            "queue_time": round(downtime_hours, 4),
            "downtime_hours": round(downtime_hours, 4),
            "utilization": round(numeric_mean(group, availability_column), 4),
            "availability": round(numeric_mean(group, availability_column), 4),
            "performance": round(numeric_mean(group, performance_column), 4),
            "quality": round(numeric_mean(group, quality_column), 4),
            "oee": round(numeric_mean(group, oee_column), 4),
            "units_produced": round(units, 2),
            "defects": round(defects, 2),
            "defect_rate": round(defects / units, 6) if units else None,
            "throughput": round(units / actual_hours, 2) if actual_hours else None,
            "metric_basis": "OEE machine records; queue_time compatibility field represents downtime_hours",
        })

    max_downtime = max((row["downtime_hours"] for row in rows), default=0.0)
    max_availability_loss = max(
        (1.0 - row["availability"] for row in rows),
        default=0.0,
    )

    for row in rows:
        row["queue_pressure"] = round(
            row["downtime_hours"] / max_downtime
            if max_downtime else 0.0,
            4,
        )
        availability_loss = 1.0 - row["availability"]
        row["utilization_pressure"] = round(
            availability_loss / max_availability_loss
            if max_availability_loss else 0.0,
            4,
        )
        score = (
            0.60 * row["queue_pressure"]
            + 0.40 * row["utilization_pressure"]
        )
        row["pressure_score"] = round(score, 4)
        row["base_pressure_score"] = round(score, 4)
        row["avg_queue"] = row["queue_time"]
        row["score"] = row["pressure_score"]

    rows.sort(
        key=lambda item: item["pressure_score"],
        reverse=True,
    )

    for index, row in enumerate(rows, start=1):
        row["rank"] = index

    return rows


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

    if MODEL1_DATA.empty and QUALITY_DATA.empty:
        return {
            "status": "unavailable",
            "message": "No manufacturing or quality-control data is available.",
        }

    quality_columns = resolve_production_columns(
        QUALITY_DATA
    )

    if not QUALITY_DATA.empty and quality_columns.get(
        "units_inspected"
    ):
        inspected = numeric_sum(
            QUALITY_DATA,
            quality_columns["units_inspected"],
        )
        passed = (
            numeric_sum(
                QUALITY_DATA,
                quality_columns["units_passed"],
            )
            if quality_columns.get("units_passed")
            else None
        )
        defects = (
            numeric_sum(
                QUALITY_DATA,
                quality_columns["defect_count"],
            )
            if quality_columns.get("defect_count")
            else None
        )

        defect_breakdown = {}
        defect_type_column = quality_columns.get("defect_type")
        if defect_type_column:
            defect_rows = QUALITY_DATA.copy()
            defect_rows[defect_type_column] = (
                defect_rows[defect_type_column]
                .fillna("Unknown")
                .replace("", "Unknown")
            )
            defect_breakdown = {
                str(label): int(count)
                for label, count in defect_rows[
                    defect_type_column
                ].value_counts().items()
                if str(label).lower() not in {"none", "unknown"}
            }

        return {
            "status": "success",
            "data_source": "product-quality-control.csv",
            "total_parts": round(inspected, 2),
            "units_inspected": round(inspected, 2),
            "units_passed": round(passed, 2) if passed is not None else None,
            "average_units_per_batch": round(
                inspected / len(QUALITY_DATA),
                2,
            ) if len(QUALITY_DATA) else None,
            "average_parts_per_hour": None,
            "average_demand": None,
            "total_defects": round(defects, 2) if defects is not None else None,
            "defect_breakdown": defect_breakdown,
            "measured_defect_rate": round(
                defects / inspected,
                6,
            ) if defects is not None and inspected else None,
            "quality_batches": int(len(QUALITY_DATA)),
            "demand_available": False,
            "message": (
                "Production volume and quality metrics use the quality-control dataset. "
                "Hourly throughput and demand are not present in that file."
            ),
        }
        return {

            "status": "unavailable"

        }


    columns = resolve_production_columns(
        MODEL1_DATA
    )

    if columns.get("machine_id"):
        total_parts = numeric_sum(
            MODEL1_DATA,
            columns["total_parts"],
        )
        actual_hours = numeric_sum(
            MODEL1_DATA,
            columns["actual_hours"],
        )
        defects = numeric_sum(
            MODEL1_DATA,
            columns["defects"],
        )

        return {
            "status": "success",
            "data_source": "manufacturing-oee.csv",
            "total_parts": round(total_parts, 2),
            "average_parts_per_hour": round(
                total_parts / actual_hours,
                2,
            ) if actual_hours else None,
            "average_demand": None,
            "total_defects": round(defects, 2),
            "measured_defect_rate": round(
                defects / total_parts,
                6,
            ) if total_parts else None,
            "actual_hours": round(actual_hours, 2),
            "demand_available": False,
            "message": "Demand is not available in the OEE dataset.",
        }

    missing = [
        field
        for field in (
            "total_parts",
            "parts_per_hour",
            "demand",
        )
        if not columns[field]
    ]

    if missing:
        return {
            "status": "unavailable",
            "message": (
                "Required production fields are missing: "
                + ", ".join(missing)
            ),
            "available_headers": export_headers(
                MODEL1_DATA
            ),
        }

    total_parts = numeric_sum(
        MODEL1_DATA,
        columns["total_parts"],
    )

    average_parts_per_hour = numeric_mean(
        MODEL1_DATA,
        columns["parts_per_hour"],
    )

    average_demand = numeric_mean(
        MODEL1_DATA,
        columns["demand"],
    )


    return {

        "status": "success",

        "total_parts": round(
            total_parts,
            2,
        ),

        "average_parts_per_hour": (
            round(average_parts_per_hour, 2)
            if average_parts_per_hour is not None
            else None
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


    columns = resolve_production_columns(
        QUALITY_DATA
    )

    measured_defect_rate = None
    if (
        not QUALITY_DATA.empty
        and columns.get("defect_count")
        and columns.get("units_inspected")
    ):
        total_units = numeric_sum(
            QUALITY_DATA,
            columns["units_inspected"],
        )
        total_defects = numeric_sum(
            QUALITY_DATA,
            columns["defect_count"],
        )
        measured_defect_rate = (
            total_defects / total_units
            if total_units
            else None
        )

    # Use the measured OEE defect rate when available; otherwise retain
    # the configurable demo assumption for legacy datasets.
    defect_rate = (
        measured_defect_rate
        if measured_defect_rate is not None
        else 0.05
    )

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
        queue_time
        if bottleneck
        and bottleneck.get("metric_basis", "").startswith("OEE")
        else queue_time / 60.0
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

        "average_parts_per_hour": (
            round(average_parts_per_hour, 2)
            if average_parts_per_hour is not None
            else None
        ),

        "assumed_defect_rate": (
            defect_rate
        ),

        "measured_defect_rate": measured_defect_rate,

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

        "total_estimated_impact": round(
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


class LoginRequest(BaseModel):
    employee_id: str
    password: str


@app.post("/login")
def login(payload: LoginRequest):
    """Backend authentication for the employee login."""
    expected_employee_id = os.getenv("INDUSTRIAL_EMPLOYEE_ID", "EMP001")
    expected_password = os.getenv("INDUSTRIAL_EMPLOYEE_PASSWORD", "Industrial@123")

    employee_id = payload.employee_id.strip()

    if employee_id != expected_employee_id or payload.password != expected_password:
        raise HTTPException(status_code=401, detail="Invalid Employee ID or Password.")

    return {
        "status": "success",
        "message": "Login successful.",
        "employee_id": employee_id,
    }


class SimulationRequest(BaseModel):
    # Existing frontend-compatible controls.
    throughput_change_percent: float = 0.0
    defect_reduction_percent: float = 0.0
    downtime_reduction_percent: float = 0.0

    # New scenario-based simulation.
    scenario: Optional[str] = None
    scenario_name: Optional[str] = None

    # Optional direct controls.
    queue_reduction_percent: float = 0.0
    utilization_change_percent: float = 0.0


def get_simulation_parameters():
    """Build simulation inputs from the real project datasets."""

    production = calculate_production_summary()
    process = calculate_process_analysis()

    defect_rate = production.get("measured_defect_rate")
    if defect_rate is None:
        defect_rate = 0.05

    model1_columns = resolve_production_columns(MODEL1_DATA)

    total_parts = production.get("total_parts") or 0.0
    parts_per_hour = None

    if model1_columns.get("parts_per_hour"):
        parts_per_hour = numeric_mean(
            MODEL1_DATA,
            model1_columns["parts_per_hour"],
        )

    if not parts_per_hour:
        parts_per_hour = production.get("average_parts_per_hour") or 0.0

    top_process = process[0] if process else None

    queue_time = (
        safe_float(top_process.get("queue_time"))
        if top_process
        else 0.0
    )

    utilization = (
        safe_float(top_process.get("utilization"))
        if top_process
        else 0.0
    )

    downtime_hours = 0.0

    if top_process and top_process.get("metric_basis", "").startswith("OEE"):
        downtime_hours = queue_time

    return ProductionParameters(
        total_parts=float(total_parts),
        parts_per_hour=float(parts_per_hour),
        defect_rate=float(defect_rate),
        queue_time=float(queue_time),
        utilization=float(utilization),
        downtime_hours=float(downtime_hours),
        scrap_cost_per_part=250.0,
        rework_cost_per_part=100.0,
        downtime_cost_per_hour=1500.0,
    )


def run_simulation(payload: SimulationRequest):
    """Run the real Python what-if simulation engine."""

    parameters = get_simulation_parameters()

    simulator = WhatIfSimulator(
        scrap_cost_per_part=parameters.scrap_cost_per_part,
        rework_cost_per_part=parameters.rework_cost_per_part,
        downtime_cost_per_hour=parameters.downtime_cost_per_hour,
    )

    requested_scenario = payload.scenario_name or payload.scenario

    # ------------------------------------------------------------
    # Predefined scenario mode
    # ------------------------------------------------------------
    if requested_scenario:
        try:
            result = simulator.compare(
                parameters,
                requested_scenario,
            )

            result["input"] = {
                "mode": "scenario",
                "scenario": requested_scenario,
            }

            return result

        except ValueError as error:
            return {
                "status": "simulation_failed",
                "message": str(error),
                "available_scenarios": [
                    item["id"] for item in list_scenarios()
                ],
            }

    # ------------------------------------------------------------
    # Existing frontend control mode
    # ------------------------------------------------------------
    custom_scenario = Scenario(
        name="Custom What-If",
        description="User-configured production what-if scenario.",
        throughput_change_percent=payload.throughput_change_percent,
        defect_rate_change_percent=-payload.defect_reduction_percent,
        utilization_change_percent=payload.utilization_change_percent,
        queue_change_percent=-payload.queue_reduction_percent,
        downtime_change_percent=-payload.downtime_reduction_percent,
    )

    baseline = simulator._run_baseline(parameters)
    simulated = simulator._run_scenario(
        parameters,
        custom_scenario,
    )

    difference = WhatIfSimulator._difference

    comparison = {
        "defective_parts": difference(
            baseline["defective_parts"],
            simulated["defective_parts"],
        ),
        "good_parts": difference(
            baseline["good_parts"],
            simulated["good_parts"],
        ),
        "effective_throughput": difference(
            baseline["effective_throughput"],
            simulated["effective_throughput"],
        ),
        "defect_rate": difference(
            baseline["defect_rate"],
            simulated["defect_rate"],
        ),
        "queue_time": difference(
            baseline["queue_time"],
            simulated["queue_time"],
        ),
        "utilization": difference(
            baseline["utilization"],
            simulated["utilization"],
        ),
        "downtime_hours": difference(
            baseline["downtime_hours"],
            simulated["downtime_hours"],
        ),
        "economic_impact": difference(
            baseline["estimated_economic_impact"],
            simulated["estimated_economic_impact"],
        ),
    }

    return {
        "status": "simulation_complete",
        "scenario": {
            "id": "custom",
            "name": custom_scenario.name,
            "description": custom_scenario.description,
        },
        "baseline": baseline,
        "simulated": simulated,
        "scenario_result": simulated,
        "comparison": comparison,
        "changes": {
            "throughput_change_percent": payload.throughput_change_percent,
            "defect_reduction_percent": payload.defect_reduction_percent,
            "downtime_reduction_percent": payload.downtime_reduction_percent,
            "queue_reduction_percent": payload.queue_reduction_percent,
            "utilization_change_percent": payload.utilization_change_percent,
        },
        "input": {
            "mode": "custom",
        },
        "decision_support_note": (
            "Simulation results are estimated outcomes based on "
            "configurable assumptions. They should be validated "
            "against real production trials before operational decisions."
        ),
    }


def simulation_scenarios():
    """Return predefined scenarios available to the frontend."""

    return {
        "status": "success",
        "scenarios": list_scenarios(),
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

        "quality_data_loaded": (
            not QUALITY_DATA.empty
        ),

        "latest_inspection": (
            LATEST_INSPECTION is not None
        ),

    }


@app.get("/data/headers")
def data_headers():
    return {
        "status": "success",
        "data_source": "product-quality-control.csv",
        "datasets": {
            "model1": {
                "headers": export_headers(MODEL1_DATA),
                "resolved_fields": resolve_production_columns(
                    MODEL1_DATA
                ),
            },
            "model2": {
                "headers": export_headers(MODEL2_DATA),
                "station_fields": discover_station_columns(
                    MODEL2_DATA
                ),
            },
            "manufacturing_oee": {
                "headers": export_headers(MANUFACTURING_DATA),
                "resolved_fields": resolve_production_columns(
                    MANUFACTURING_DATA
                ),
            },
            "quality_control": {
                "headers": export_headers(QUALITY_DATA),
                "resolved_fields": resolve_production_columns(
                    QUALITY_DATA
                ),
            },
        },
        "note": (
            "Headers are discovered from the first CSV row. "
            "Known aliases are mapped to the canonical analytics fields."
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

@app.get("/simulation/scenarios")
def simulation_scenarios_endpoint():

    return simulation_scenarios()


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