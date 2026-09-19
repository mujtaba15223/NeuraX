from pathlib import Path

import pandas as pd


# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

MODEL2_PATH = (
    BASE_DIR
    / "data"
    / "raw"
    / "model2"
    / "Model_2.csv"
)


# ============================================================
# PROCESS VARIABLES
# ============================================================

PROCESS_VARIABLES = {
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
# LOAD DATA
# ============================================================

def load_process_data():

    return pd.read_csv(
        MODEL2_PATH
    )


# ============================================================
# CORRELATION ANALYSIS
# ============================================================

def calculate_process_correlations():

    df = load_process_data()

    correlation_results = []

    for station, variables in PROCESS_VARIABLES.items():

        queue_column = variables["queue"]

        utilization_column = variables["utilization"]

        queue_correlations = {}

        utilization_correlations = {}

        for target_station, target_variables in PROCESS_VARIABLES.items():

            target_queue = target_variables["queue"]

            target_utilization = (
                target_variables["utilization"]
            )

            queue_corr = df[
                queue_column
            ].corr(
                df[target_queue]
            )

            utilization_corr = df[
                utilization_column
            ].corr(
                df[target_utilization]
            )

            queue_correlations[
                target_station
            ] = round(
                float(queue_corr),
                4,
            )

            utilization_correlations[
                target_station
            ] = round(
                float(utilization_corr),
                4,
            )

        correlation_results.append(
            {
                "station": station,

                "queue_correlations": (
                    queue_correlations
                ),

                "utilization_correlations": (
                    utilization_correlations
                ),
            }
        )

    return correlation_results


# ============================================================
# DEFECT-PROCESS ASSOCIATION
# ============================================================

def calculate_defect_process_association(
    defect_type="scratch"
):
    """
    Provide process-level association signals for a detected
    defect.

    The current public process dataset does not contain a
    defect label linked to individual production records.
    Therefore, this function does NOT claim a statistical
    defect-to-process correlation.

    Instead, it reports the process pressure signals that
    should be investigated alongside the visual defect.
    """

    df = load_process_data()

    results = []

    for station, variables in PROCESS_VARIABLES.items():

        queue_column = variables["queue"]

        utilization_column = (
            variables["utilization"]
        )

        queue_mean = float(
            df[queue_column].mean()
        )

        utilization_mean = float(
            df[utilization_column].mean()
        )

        queue_std = float(
            df[queue_column].std()
        )

        utilization_std = float(
            df[utilization_column].std()
        )

        results.append(
            {
                "defect": defect_type,

                "station": station,

                "queue_mean": round(
                    queue_mean,
                    4,
                ),

                "utilization_mean": round(
                    utilization_mean,
                    4,
                ),

                "queue_std": round(
                    queue_std,
                    4,
                ),

                "utilization_std": round(
                    utilization_std,
                    4,
                ),

                "evidence_type": (
                    "process_pressure"
                ),

                "interpretation": (
                    "Process signal requiring "
                    "investigation alongside "
                    "visual defect evidence."
                ),
            }
        )

    return results


# ============================================================
# STRONGEST PROCESS SIGNAL
# ============================================================

def get_strongest_process_signal():

    df = load_process_data()

    signals = []

    for station, variables in PROCESS_VARIABLES.items():

        queue_mean = float(
            df[variables["queue"]].mean()
        )

        utilization_mean = float(
            df[variables["utilization"]].mean()
        )

        signals.append(
            {
                "station": station,
                "queue_mean": queue_mean,
                "utilization_mean": utilization_mean,
            }
        )

    max_queue = max(
        item["queue_mean"]
        for item in signals
    )

    max_utilization = max(
        item["utilization_mean"]
        for item in signals
    )

    for item in signals:

        queue_pressure = (
            item["queue_mean"] / max_queue
            if max_queue > 0
            else 0.0
        )

        utilization_pressure = (
            item["utilization_mean"]
            / max_utilization
            if max_utilization > 0
            else 0.0
        )

        item["queue_pressure"] = round(
            queue_pressure,
            4,
        )

        item["utilization_pressure"] = round(
            utilization_pressure,
            4,
        )

        item["combined_pressure"] = round(
            0.60 * queue_pressure
            + 0.40 * utilization_pressure,
            4,
        )

    signals.sort(
        key=lambda item: item[
            "combined_pressure"
        ],
        reverse=True,
    )

    return signals[0]


# ============================================================
# CLI TEST
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("PROCESS CORRELATION ANALYSIS")
    print("=" * 60)

    correlations = (
        calculate_process_correlations()
    )

    for result in correlations:

        print()
        print(
            f"Station: {result['station']}"
        )

        print(
            "Queue correlations:"
        )

        for (
            station,
            value,
        ) in result[
            "queue_correlations"
        ].items():

            print(
                f"  {station}: {value}"
            )

        print(
            "Utilization correlations:"
        )

        for (
            station,
            value,
        ) in result[
            "utilization_correlations"
        ].items():

            print(
                f"  {station}: {value}"
            )

    print()
    print("=" * 60)
    print("STRONGEST PROCESS SIGNAL")
    print("=" * 60)

    strongest = (
        get_strongest_process_signal()
    )

    print(
        f"Station: {strongest['station']}"
    )

    print(
        f"Combined Pressure: "
        f"{strongest['combined_pressure']}"
    )

    print()
    print(
        "Important: correlation and process "
        "pressure are evidence for investigation, "
        "not proof of causality."
    )