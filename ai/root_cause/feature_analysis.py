from pathlib import Path

import pandas as pd


# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

MANUFACTURING_OEE_PATH = (
    BASE_DIR
    / "data"
    / "raw"
    / "new"
    / "manufacturing-oee.csv"
)


# ============================================================
# PROCESS FEATURES
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
# LOAD PROCESS DATA
# ============================================================

def load_process_data():
    """
    Load Model 2 manufacturing process data.
    """

    return pd.read_csv(MANUFACTURING_OEE_PATH)


# ============================================================
# FEATURE ANALYSIS
# ============================================================

def analyze_process_features():
    """
    Calculate process-level evidence that can be used
    by the root-cause analysis pipeline.

    The output describes association/pressure signals.
    It does not establish manufacturing causality.
    """

    df = load_process_data()

    if "machine_id" in df.columns:
        grouped = df.groupby("machine_id", dropna=True)
        machine_rows = []

        for machine, group in grouped:
            planned = pd.to_numeric(group["planned_hours"], errors="coerce").sum()
            actual = pd.to_numeric(group["actual_hours"], errors="coerce").sum()
            downtime = max(0.0, float(planned - actual))
            availability = float(pd.to_numeric(group["availability_pct"], errors="coerce").mean())
            machine_rows.append((str(machine), downtime, availability))

        max_downtime = max((row[1] for row in machine_rows), default=0.0)
        max_loss = max((1.0 - row[2] for row in machine_rows), default=0.0)
        results = []

        for station, downtime, availability in machine_rows:
            queue_pressure = downtime / max_downtime if max_downtime else 0.0
            utilization_pressure = (1.0 - availability) / max_loss if max_loss else 0.0
            combined_pressure = 0.60 * queue_pressure + 0.40 * utilization_pressure
            results.append({
                "station": station,
                "queue_time": round(downtime, 4),
                "utilization": round(availability, 4),
                "queue_pressure": round(queue_pressure, 4),
                "utilization_pressure": round(utilization_pressure, 4),
                "combined_pressure": round(combined_pressure, 4),
                "metric_basis": "OEE machine records; queue_time represents downtime_hours",
            })

        results.sort(key=lambda item: item["combined_pressure"], reverse=True)
        for rank, result in enumerate(results, start=1):
            result["rank"] = rank
        return results

    average_queue = {
        station: float(df[features["queue"]].mean())
        for station, features in STATIONS.items()
    }

    average_utilization = {
        station: float(df[features["utilization"]].mean())
        for station, features in STATIONS.items()
    }

    max_queue = max(
        average_queue.values()
    )

    max_utilization = max(
        average_utilization.values()
    )

    results = []

    for station, features in STATIONS.items():

        queue = average_queue[station]

        utilization = (
            average_utilization[station]
        )

        queue_pressure = (
            queue / max_queue
            if max_queue > 0
            else 0.0
        )

        utilization_pressure = (
            utilization / max_utilization
            if max_utilization > 0
            else 0.0
        )

        combined_pressure = (
            0.60 * queue_pressure
            + 0.40 * utilization_pressure
        )

        results.append(
            {
                "station": station,

                "queue_time": round(
                    queue,
                    4,
                ),

                "utilization": round(
                    utilization,
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

                "combined_pressure": round(
                    combined_pressure,
                    4,
                ),
            }
        )

    results.sort(
        key=lambda item: item[
            "combined_pressure"
        ],
        reverse=True,
    )

    for rank, result in enumerate(
        results,
        start=1,
    ):
        result["rank"] = rank

    return results


# ============================================================
# TOP PROCESS SIGNAL
# ============================================================

def get_top_process_signal():
    """
    Return the strongest process pressure signal.
    """

    results = analyze_process_features()

    if not results:
        return None

    return results[0]


# ============================================================
# CLI TEST
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("ROOT CAUSE FEATURE ANALYSIS")
    print("=" * 60)

    results = analyze_process_features()

    for result in results:

        print()
        print(
            f"Rank {result['rank']}: "
            f"{result['station']}"
        )

        print(
            f"Queue Time: "
            f"{result['queue_time']}"
        )

        print(
            f"Utilization: "
            f"{result['utilization']}"
        )

        print(
            f"Queue Pressure: "
            f"{result['queue_pressure']}"
        )

        print(
            f"Utilization Pressure: "
            f"{result['utilization_pressure']}"
        )

        print(
            f"Combined Pressure: "
            f"{result['combined_pressure']}"
        )

    print()
    print("=" * 60)
    print("TOP PROCESS SIGNAL")
    print("=" * 60)

    top_signal = get_top_process_signal()

    if top_signal:

        print(
            f"Station: "
            f"{top_signal['station']}"
        )

        print(
            f"Pressure: "
            f"{top_signal['combined_pressure']}"
        )

    print()
    print(
        "Note: Process pressure is evidence for "
        "investigation, not proof of causality."
    )