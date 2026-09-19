from pathlib import Path

import pandas as pd


# ============================================================
# Production Impact & Economic Impact Analyzer
# ============================================================

MODEL1_PATH = Path(
    "data/raw/model1/Model_1.csv"
)


# ------------------------------------------------------------
# Configurable economic assumptions
# ------------------------------------------------------------

SCRAP_COST_PER_PART = 250.0
REWORK_COST_PER_PART = 100.0
DOWNTIME_COST_PER_HOUR = 1500.0


# ------------------------------------------------------------
# Load production data
# ------------------------------------------------------------

def load_production_data():

    df = pd.read_csv(
        MODEL1_PATH
    )

    return df


# ------------------------------------------------------------
# Production metrics
# ------------------------------------------------------------

def calculate_production_metrics(df):

    total_parts = df[
        "Total parts"
    ].sum()

    average_parts_per_hour = df[
        "Parts per hour"
    ].mean()

    total_demand = df[
        "Demand"
    ].sum()

    average_demand = df[
        "Demand"
    ].mean()

    return {
        "total_parts": total_parts,
        "average_parts_per_hour":
            average_parts_per_hour,
        "total_demand": total_demand,
        "average_demand":
            average_demand,
    }


# ------------------------------------------------------------
# Estimate defect impact
# ------------------------------------------------------------

def estimate_defect_impact(
    total_parts,
    defect_rate
):

    estimated_defective_parts = (
        total_parts * defect_rate
    )

    estimated_scrap_cost = (
        estimated_defective_parts
        * SCRAP_COST_PER_PART
    )

    estimated_rework_cost = (
        estimated_defective_parts
        * REWORK_COST_PER_PART
    )

    return {
        "estimated_defective_parts":
            estimated_defective_parts,

        "estimated_scrap_cost":
            estimated_scrap_cost,

        "estimated_rework_cost":
            estimated_rework_cost,
    }


# ------------------------------------------------------------
# Estimate bottleneck impact
# ------------------------------------------------------------

def estimate_bottleneck_impact(
    df
):

    drilling_waiting = df[
        "Drilling Waiting Time"
    ].mean()

    assembly_waiting = df[
        "Assembly Waiting Time"
    ].mean()

    milling_waiting = df[
        "Milling Waiting Time"
    ].mean()

    waiting_times = {
        "Drilling": drilling_waiting,
        "Milling": milling_waiting,
        "Assembly": assembly_waiting,
    }

    bottleneck_station = max(
        waiting_times,
        key=waiting_times.get
    )

    bottleneck_waiting = (
        waiting_times[
            bottleneck_station
        ]
    )

    return {
        "station":
            bottleneck_station,

        "average_waiting_time":
            bottleneck_waiting,

        "all_waiting_times":
            waiting_times,
    }


# ------------------------------------------------------------
# Combined impact
# ------------------------------------------------------------

def calculate_total_impact(
    defect_impact,
    bottleneck_waiting
):

    estimated_downtime_cost = (
        bottleneck_waiting
        / 60.0
        * DOWNTIME_COST_PER_HOUR
    )

    total_cost = (
        defect_impact[
            "estimated_scrap_cost"
        ]
        +
        defect_impact[
            "estimated_rework_cost"
        ]
        +
        estimated_downtime_cost
    )

    return {
        "downtime_cost":
            estimated_downtime_cost,

        "total_estimated_cost":
            total_cost,
    }


# ------------------------------------------------------------
# Print report
# ------------------------------------------------------------

def print_report(
    production_metrics,
    defect_impact,
    bottleneck_impact,
    total_impact,
    defect_rate
):

    print("\n" + "=" * 70)
    print(
        "PRODUCTION & ECONOMIC IMPACT"
    )
    print("=" * 70)

    print("\nProduction metrics:")

    print(
        f"  Total parts: "
        f"{production_metrics['total_parts']:.0f}"
    )

    print(
        f"  Average parts/hour: "
        f"{production_metrics['average_parts_per_hour']:.2f}"
    )

    print(
        f"  Average demand: "
        f"{production_metrics['average_demand']:.2f}"
    )

    print("\nDefect assumptions:")

    print(
        f"  Assumed defect rate: "
        f"{defect_rate * 100:.2f}%"
    )

    print(
        f"  Estimated defective parts: "
        f"{defect_impact['estimated_defective_parts']:.2f}"
    )

    print("\nEstimated defect cost:")

    print(
        f"  Scrap cost: "
        f"₹{defect_impact['estimated_scrap_cost']:,.2f}"
    )

    print(
        f"  Rework cost: "
        f"₹{defect_impact['estimated_rework_cost']:,.2f}"
    )

    print("\nBottleneck evidence:")

    print(
        f"  Station: "
        f"{bottleneck_impact['station']}"
    )

    print(
        f"  Average waiting time: "
        f"{bottleneck_impact['average_waiting_time']:.2f}"
    )

    print("\nEstimated downtime cost:")

    print(
        f"  ₹{total_impact['downtime_cost']:,.2f}"
    )

    print("\nTOTAL ESTIMATED IMPACT:")

    print(
        f"  ₹{total_impact['total_estimated_cost']:,.2f}"
    )

    print("\nIMPORTANT:")

    print(
        "  Economic values are configurable "
        "assumptions for decision support."
    )

    print(
        "  They are not claimed as actual "
        "financial losses."
    )

    print("=" * 70)


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

def main():

    print(
        "\nLoading production data..."
    )

    df = load_production_data()

    print(
        f"Loaded {len(df)} production records."
    )

    production_metrics = (
        calculate_production_metrics(
            df
        )
    )

    # Demo assumption.
    # Later this will come from the vision
    # inspection pipeline.
    defect_rate = 0.05

    defect_impact = (
        estimate_defect_impact(
            production_metrics[
                "total_parts"
            ],
            defect_rate
        )
    )

    bottleneck_impact = (
        estimate_bottleneck_impact(
            df
        )
    )

    total_impact = (
        calculate_total_impact(
            defect_impact,
            bottleneck_impact[
                "average_waiting_time"
            ]
        )
    )

    print_report(
        production_metrics,
        defect_impact,
        bottleneck_impact,
        total_impact,
        defect_rate
    )


if __name__ == "__main__":
    main()