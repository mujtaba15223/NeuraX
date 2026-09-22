"""
What-If Simulation Engine

Compares current production conditions against an industrial
improvement scenario.

The engine is designed for decision support:
it estimates possible outcomes and does not claim causal certainty.
"""

from __future__ import annotations

from typing import Any, Dict

from .production_simulation import (
    ProductionParameters,
    ProductionSimulator,
)

from .scenarios import (
    Scenario,
    get_scenario,
    apply_scenario,
)


class WhatIfSimulator:
    """Runs baseline vs scenario comparisons."""

    def __init__(
        self,
        scrap_cost_per_part: float = 250.0,
        rework_cost_per_part: float = 100.0,
        downtime_cost_per_hour: float = 1500.0,
    ) -> None:

        self.simulator = ProductionSimulator(
            scrap_cost_per_part=scrap_cost_per_part,
            rework_cost_per_part=rework_cost_per_part,
            downtime_cost_per_hour=downtime_cost_per_hour,
        )

    # ------------------------------------------------------------------
    # Baseline
    # ------------------------------------------------------------------

    def _run_baseline(
        self,
        parameters: ProductionParameters,
    ) -> Dict[str, Any]:

        return self.simulator.simulate(parameters)

    # ------------------------------------------------------------------
    # Scenario
    # ------------------------------------------------------------------

    def _run_scenario(
        self,
        parameters: ProductionParameters,
        scenario: Scenario,
    ) -> Dict[str, Any]:

        baseline_values = {
            "parts_per_hour": parameters.parts_per_hour,
            "defect_rate": parameters.defect_rate,
            "utilization": parameters.utilization,
            "queue_time": parameters.queue_time,
            "downtime_hours": parameters.downtime_hours,
        }

        modified_values = apply_scenario(
            scenario,
            baseline_values,
        )

        scenario_parameters = ProductionParameters(
            total_parts=parameters.total_parts,

            parts_per_hour=modified_values.get(
                "parts_per_hour",
                parameters.parts_per_hour,
            ),

            defect_rate=modified_values.get(
                "defect_rate",
                parameters.defect_rate,
            ),

            queue_time=modified_values.get(
                "queue_time",
                parameters.queue_time,
            ),

            utilization=modified_values.get(
                "utilization",
                parameters.utilization,
            ),

            downtime_hours=modified_values.get(
                "downtime_hours",
                parameters.downtime_hours,
            ),

            scrap_cost_per_part=parameters.scrap_cost_per_part,

            rework_cost_per_part=parameters.rework_cost_per_part,

            downtime_cost_per_hour=parameters.downtime_cost_per_hour,
        )

        return self.simulator.simulate(
            scenario_parameters
        )

    # ------------------------------------------------------------------
    # Difference calculations
    # ------------------------------------------------------------------

    @staticmethod
    def _difference(
        baseline: float,
        scenario: float,
    ) -> Dict[str, float]:

        absolute = float(scenario) - float(baseline)

        if baseline == 0:
            percentage = 0.0
        else:
            percentage = (
                absolute / abs(float(baseline))
            ) * 100.0

        return {
            "absolute": round(absolute, 4),
            "percentage": round(percentage, 2),
        }

    # ------------------------------------------------------------------
    # Main comparison
    # ------------------------------------------------------------------

    def compare(
        self,
        parameters: ProductionParameters,
        scenario_name: str,
    ) -> Dict[str, Any]:
        """
        Compare baseline production against a selected scenario.
        """

        scenario = get_scenario(
            scenario_name
        )

        baseline = self._run_baseline(
            parameters
        )

        simulated = self._run_scenario(
            parameters,
            scenario,
        )

        comparison = {
            "defective_parts": self._difference(
                baseline["defective_parts"],
                simulated["defective_parts"],
            ),

            "good_parts": self._difference(
                baseline["good_parts"],
                simulated["good_parts"],
            ),

            "effective_throughput": self._difference(
                baseline["effective_throughput"],
                simulated["effective_throughput"],
            ),

            "defect_rate": self._difference(
                baseline["defect_rate"],
                simulated["defect_rate"],
            ),

            "queue_time": self._difference(
                baseline["queue_time"],
                simulated["queue_time"],
            ),

            "utilization": self._difference(
                baseline["utilization"],
                simulated["utilization"],
            ),

            "downtime_hours": self._difference(
                baseline["downtime_hours"],
                simulated["downtime_hours"],
            ),

            "economic_impact": self._difference(
                baseline["estimated_economic_impact"],
                simulated["estimated_economic_impact"],
            ),
        }

        return {
            "status": "success",

            "scenario": {
                "id": scenario_name,
                "name": scenario.name,
                "description": scenario.description,
            },

            "baseline": baseline,

            "simulated": simulated,

            "comparison": comparison,

            "interpretation": self._generate_interpretation(
                baseline,
                simulated,
            ),

            "decision_support_note": (
                "Simulation results are estimated outcomes based "
                "on configurable assumptions. They should be "
                "validated against real production trials before "
                "operational decisions."
            ),
        }

    # ------------------------------------------------------------------
    # Interpretation
    # ------------------------------------------------------------------

    @staticmethod
    def _generate_interpretation(
        baseline: Dict[str, Any],
        simulated: Dict[str, Any],
    ) -> Dict[str, Any]:

        throughput_change = (
            simulated["effective_throughput"]
            - baseline["effective_throughput"]
        )

        defect_change = (
            simulated["defective_parts"]
            - baseline["defective_parts"]
        )

        economic_change = (
            simulated["estimated_economic_impact"]
            - baseline["estimated_economic_impact"]
        )

        if throughput_change > 0:
            throughput_direction = "increase"
        elif throughput_change < 0:
            throughput_direction = "decrease"
        else:
            throughput_direction = "no_change"

        if defect_change < 0:
            defect_direction = "reduction"
        elif defect_change > 0:
            defect_direction = "increase"
        else:
            defect_direction = "no_change"

        if economic_change < 0:
            economic_direction = "lower"
        elif economic_change > 0:
            economic_direction = "higher"
        else:
            economic_direction = "unchanged"

        return {
            "throughput": {
                "direction": throughput_direction,
                "change": round(
                    throughput_change,
                    2,
                ),
            },

            "defects": {
                "direction": defect_direction,
                "change": round(
                    defect_change,
                    2,
                ),
            },

            "economic_impact": {
                "direction": economic_direction,
                "change": round(
                    economic_change,
                    2,
                ),
            },
        }


# ----------------------------------------------------------------------
# Convenience function
# ----------------------------------------------------------------------

def run_what_if(
    parameters: ProductionParameters,
    scenario_name: str,
) -> Dict[str, Any]:
    """
    Convenience wrapper for the what-if engine.
    """

    engine = WhatIfSimulator(
        scrap_cost_per_part=parameters.scrap_cost_per_part,
        rework_cost_per_part=parameters.rework_cost_per_part,
        downtime_cost_per_hour=parameters.downtime_cost_per_hour,
    )

    return engine.compare(
        parameters,
        scenario_name,
    )


# ----------------------------------------------------------------------
# Example standalone test
# ----------------------------------------------------------------------

if __name__ == "__main__":

    parameters = ProductionParameters(
        total_parts=257155,
        parts_per_hour=209.45,
        defect_rate=0.043417,
        queue_time=2.4623,
        utilization=0.521,
        downtime_hours=0.041,
    )

    result = run_what_if(
        parameters,
        "process_optimization",
    )

    print("\nWHAT-IF SIMULATION")
    print("=" * 60)

    print(
        f"Scenario: "
        f"{result['scenario']['name']}"
    )

    print(
        f"\nBaseline throughput: "
        f"{result['baseline']['effective_throughput']}"
    )

    print(
        f"Simulated throughput: "
        f"{result['simulated']['effective_throughput']}"
    )

    print(
        f"\nBaseline defects: "
        f"{result['baseline']['defective_parts']}"
    )

    print(
        f"Simulated defects: "
        f"{result['simulated']['defective_parts']}"
    )

    print(
        f"\nBaseline economic impact: "
        f"₹{result['baseline']['estimated_economic_impact']:,.2f}"
    )

    print(
        f"Simulated economic impact: "
        f"₹{result['simulated']['estimated_economic_impact']:,.2f}"
    )