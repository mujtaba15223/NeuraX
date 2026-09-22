"""
Industrial Simulation Scenarios

Defines reusable what-if scenarios for the
Industrial Defect Root-Cause AI system.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class Scenario:
    """Represents a production what-if scenario."""

    name: str
    description: str

    throughput_change_percent: float = 0.0
    defect_rate_change_percent: float = 0.0
    utilization_change_percent: float = 0.0
    queue_change_percent: float = 0.0
    downtime_change_percent: float = 0.0


# ----------------------------------------------------------------------
# Predefined industrial scenarios
# ----------------------------------------------------------------------

SCENARIOS: Dict[str, Scenario] = {

    "baseline": Scenario(
        name="Baseline",
        description="Current observed production conditions.",
    ),

    "reduce_defects": Scenario(
        name="Reduce Defects",
        description=(
            "Improve inspection and process control to reduce "
            "the defect rate."
        ),
        defect_rate_change_percent=-25.0,
    ),

    "reduce_queue": Scenario(
        name="Reduce Queue",
        description=(
            "Improve material flow and reduce waiting time "
            "at the constrained process."
        ),
        queue_change_percent=-25.0,
    ),

    "increase_capacity": Scenario(
        name="Increase Capacity",
        description=(
            "Increase effective production capacity at the "
            "constrained process."
        ),
        throughput_change_percent=15.0,
        utilization_change_percent=-5.0,
    ),

    "process_optimization": Scenario(
        name="Process Optimization",
        description=(
            "Combined process improvement reducing queue pressure "
            "and defect rate while improving throughput."
        ),
        throughput_change_percent=10.0,
        defect_rate_change_percent=-15.0,
        queue_change_percent=-20.0,
        utilization_change_percent=-3.0,
    ),

    "maintenance": Scenario(
        name="Preventive Maintenance",
        description=(
            "Reduce unexpected downtime through preventive "
            "maintenance."
        ),
        downtime_change_percent=-30.0,
    ),

    "quality_and_flow": Scenario(
        name="Quality + Flow Improvement",
        description=(
            "Combined quality improvement and production-flow "
            "optimization."
        ),
        throughput_change_percent=8.0,
        defect_rate_change_percent=-20.0,
        queue_change_percent=-20.0,
        downtime_change_percent=-15.0,
    ),
}


# ----------------------------------------------------------------------
# Scenario utilities
# ----------------------------------------------------------------------

def get_scenario(name: str) -> Scenario:
    """
    Return a predefined scenario.

    Raises:
        ValueError: if the scenario does not exist.
    """

    key = name.strip().lower().replace(" ", "_")

    if key not in SCENARIOS:
        available = ", ".join(SCENARIOS.keys())

        raise ValueError(
            f"Unknown scenario '{name}'. "
            f"Available scenarios: {available}"
        )

    return SCENARIOS[key]


def list_scenarios() -> list[Dict[str, Any]]:
    """Return all available scenarios."""

    return [
        {
            "id": scenario_id,
            "name": scenario.name,
            "description": scenario.description,
            "changes": {
                "throughput_change_percent": (
                    scenario.throughput_change_percent
                ),
                "defect_rate_change_percent": (
                    scenario.defect_rate_change_percent
                ),
                "utilization_change_percent": (
                    scenario.utilization_change_percent
                ),
                "queue_change_percent": (
                    scenario.queue_change_percent
                ),
                "downtime_change_percent": (
                    scenario.downtime_change_percent
                ),
            },
        }
        for scenario_id, scenario in SCENARIOS.items()
    ]


def apply_scenario(
    scenario: Scenario,
    baseline: Dict[str, float],
) -> Dict[str, float]:
    """
    Apply scenario changes to baseline production values.

    Expected baseline keys may include:

        parts_per_hour
        defect_rate
        utilization
        queue_time
        downtime_hours

    Values are modified proportionally according to the scenario.
    """

    def apply_percent(
        value: float,
        change_percent: float,
    ) -> float:
        return max(
            0.0,
            float(value) * (1.0 + change_percent / 100.0),
        )

    result = dict(baseline)

    if "parts_per_hour" in baseline:
        result["parts_per_hour"] = apply_percent(
            baseline["parts_per_hour"],
            scenario.throughput_change_percent,
        )

    if "defect_rate" in baseline:
        result["defect_rate"] = max(
            0.0,
            min(
                1.0,
                apply_percent(
                    baseline["defect_rate"],
                    scenario.defect_rate_change_percent,
                ),
            ),
        )

    if "utilization" in baseline:
        result["utilization"] = max(
            0.0,
            min(
                1.0,
                apply_percent(
                    baseline["utilization"],
                    scenario.utilization_change_percent,
                ),
            ),
        )

    if "queue_time" in baseline:
        result["queue_time"] = apply_percent(
            baseline["queue_time"],
            scenario.queue_change_percent,
        )

    if "downtime_hours" in baseline:
        result["downtime_hours"] = apply_percent(
            baseline["downtime_hours"],
            scenario.downtime_change_percent,
        )

    return result


def get_scenario_summary(name: str) -> Dict[str, Any]:
    """Return a compact description of one scenario."""

    scenario = get_scenario(name)

    return {
        "name": scenario.name,
        "description": scenario.description,
        "changes": {
            "throughput": scenario.throughput_change_percent,
            "defect_rate": scenario.defect_rate_change_percent,
            "utilization": scenario.utilization_change_percent,
            "queue_time": scenario.queue_change_percent,
            "downtime": scenario.downtime_change_percent,
        },
    }


# ----------------------------------------------------------------------
# Standalone test
# ----------------------------------------------------------------------

if __name__ == "__main__":

    print("\nAvailable Industrial Scenarios")
    print("=" * 50)

    for item in list_scenarios():
        print(f"\n{item['id']}")
        print(f"  Name: {item['name']}")
        print(f"  Description: {item['description']}")
        print(f"  Changes: {item['changes']}")