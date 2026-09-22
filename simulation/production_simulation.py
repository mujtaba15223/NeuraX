"""
Production Simulation Engine

Provides baseline production calculations and estimates the impact
of changes to throughput, utilization, queue time, defect rate,
and downtime.

Important:
- These are decision-support simulations.
- Results are estimates, not guarantees.
- Economic values are configurable assumptions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class ProductionParameters:
    """Parameters used by the production simulation."""

    total_parts: float
    parts_per_hour: float
    defect_rate: float
    queue_time: float = 0.0
    utilization: float = 0.0
    downtime_hours: float = 0.0

    scrap_cost_per_part: float = 250.0
    rework_cost_per_part: float = 100.0
    downtime_cost_per_hour: float = 1500.0


class ProductionSimulator:
    """
    Simulates production performance under configurable conditions.

    The simulator does not claim to predict a real factory exactly.
    It provides comparable baseline vs what-if estimates.
    """

    def __init__(
        self,
        scrap_cost_per_part: float = 250.0,
        rework_cost_per_part: float = 100.0,
        downtime_cost_per_hour: float = 1500.0,
    ) -> None:

        self.scrap_cost_per_part = float(scrap_cost_per_part)
        self.rework_cost_per_part = float(rework_cost_per_part)
        self.downtime_cost_per_hour = float(downtime_cost_per_hour)

    # ------------------------------------------------------------------
    # Core calculations
    # ------------------------------------------------------------------

    @staticmethod
    def _safe_rate(value: float) -> float:
        """Keep rates between 0 and 1."""
        return max(0.0, min(1.0, float(value)))

    def estimate_defective_parts(
        self,
        total_parts: float,
        defect_rate: float,
    ) -> float:
        """Estimate the number of defective parts."""

        total_parts = max(0.0, float(total_parts))
        defect_rate = self._safe_rate(defect_rate)

        return total_parts * defect_rate

    def estimate_good_parts(
        self,
        total_parts: float,
        defect_rate: float,
    ) -> float:
        """Estimate the number of good parts."""

        defective = self.estimate_defective_parts(
            total_parts,
            defect_rate,
        )

        return max(0.0, float(total_parts) - defective)

    def estimate_scrap_cost(
        self,
        defective_parts: float,
        scrap_ratio: float = 1.0,
    ) -> float:
        """
        Estimate scrap cost.

        scrap_ratio represents the fraction of defective parts
        assumed to become scrap.
        """

        defective_parts = max(0.0, float(defective_parts))
        scrap_ratio = self._safe_rate(scrap_ratio)

        return (
            defective_parts
            * scrap_ratio
            * self.scrap_cost_per_part
        )

    def estimate_rework_cost(
        self,
        defective_parts: float,
        rework_ratio: float = 1.0,
    ) -> float:
        """
        Estimate rework cost.

        rework_ratio represents the fraction of defective parts
        assumed to require rework.
        """

        defective_parts = max(0.0, float(defective_parts))
        rework_ratio = self._safe_rate(rework_ratio)

        return (
            defective_parts
            * rework_ratio
            * self.rework_cost_per_part
        )

    def estimate_downtime_cost(
        self,
        downtime_hours: float,
    ) -> float:
        """Estimate downtime cost."""

        downtime_hours = max(0.0, float(downtime_hours))

        return downtime_hours * self.downtime_cost_per_hour

    def estimate_total_economic_impact(
        self,
        defective_parts: float,
        downtime_hours: float = 0.0,
        scrap_ratio: float = 1.0,
        rework_ratio: float = 1.0,
    ) -> float:
        """Calculate total estimated economic impact."""

        scrap_cost = self.estimate_scrap_cost(
            defective_parts,
            scrap_ratio,
        )

        rework_cost = self.estimate_rework_cost(
            defective_parts,
            rework_ratio,
        )

        downtime_cost = self.estimate_downtime_cost(
            downtime_hours,
        )

        return scrap_cost + rework_cost + downtime_cost

    # ------------------------------------------------------------------
    # Throughput calculations
    # ------------------------------------------------------------------

    def estimate_effective_throughput(
        self,
        parts_per_hour: float,
        utilization: float,
        downtime_hours: float = 0.0,
    ) -> float:
        """
        Estimate effective hourly throughput.

        parts_per_hour represents nominal process throughput.
        utilization is applied as an operating factor.
        """

        parts_per_hour = max(0.0, float(parts_per_hour))
        utilization = self._safe_rate(utilization)

        # If utilization is zero, preserve the nominal rate rather
        # than forcing production to zero when the input is missing.
        if utilization == 0:
            effective_rate = parts_per_hour
        else:
            effective_rate = parts_per_hour * utilization

        downtime_factor = max(
            0.0,
            1.0 - max(0.0, float(downtime_hours)) / 24.0,
        )

        return effective_rate * downtime_factor

    def estimate_daily_output(
        self,
        parts_per_hour: float,
        utilization: float,
        operating_hours: float = 8.0,
        downtime_hours: float = 0.0,
    ) -> float:
        """Estimate daily production output."""

        operating_hours = max(0.0, float(operating_hours))

        throughput = self.estimate_effective_throughput(
            parts_per_hour,
            utilization,
            downtime_hours,
        )

        return throughput * operating_hours

    # ------------------------------------------------------------------
    # Queue / bottleneck calculations
    # ------------------------------------------------------------------

    def estimate_queue_reduction(
        self,
        baseline_queue: float,
        new_queue: float,
    ) -> float:
        """Calculate absolute queue reduction."""

        return float(baseline_queue) - float(new_queue)

    def estimate_queue_reduction_percent(
        self,
        baseline_queue: float,
        new_queue: float,
    ) -> float:
        """Calculate percentage reduction in queue time."""

        baseline_queue = float(baseline_queue)

        if baseline_queue <= 0:
            return 0.0

        reduction = self.estimate_queue_reduction(
            baseline_queue,
            new_queue,
        )

        return (reduction / baseline_queue) * 100.0

    # ------------------------------------------------------------------
    # Full simulation
    # ------------------------------------------------------------------

    def simulate(
        self,
        parameters: ProductionParameters,
    ) -> Dict[str, Any]:
        """
        Run a complete production simulation.
        """

        total_parts = max(0.0, float(parameters.total_parts))
        parts_per_hour = max(0.0, float(parameters.parts_per_hour))
        defect_rate = self._safe_rate(parameters.defect_rate)
        queue_time = max(0.0, float(parameters.queue_time))
        utilization = self._safe_rate(parameters.utilization)
        downtime_hours = max(0.0, float(parameters.downtime_hours))

        defective_parts = self.estimate_defective_parts(
            total_parts,
            defect_rate,
        )

        good_parts = self.estimate_good_parts(
            total_parts,
            defect_rate,
        )

        effective_throughput = self.estimate_effective_throughput(
            parts_per_hour,
            utilization,
            downtime_hours,
        )

        economic_impact = self.estimate_total_economic_impact(
            defective_parts,
            downtime_hours,
        )

        return {
            "total_parts": round(total_parts, 2),
            "defect_rate": round(defect_rate, 6),
            "defective_parts": round(defective_parts, 2),
            "good_parts": round(good_parts, 2),
            "parts_per_hour": round(parts_per_hour, 2),
            "utilization": round(utilization, 6),
            "effective_throughput": round(effective_throughput, 2),
            "queue_time": round(queue_time, 4),
            "downtime_hours": round(downtime_hours, 4),
            "estimated_economic_impact": round(
                economic_impact,
                2,
            ),
        }


# ----------------------------------------------------------------------
# Convenience function
# ----------------------------------------------------------------------

def run_production_simulation(
    total_parts: float,
    parts_per_hour: float,
    defect_rate: float,
    queue_time: float = 0.0,
    utilization: float = 0.0,
    downtime_hours: float = 0.0,
    scrap_cost_per_part: float = 250.0,
    rework_cost_per_part: float = 100.0,
    downtime_cost_per_hour: float = 1500.0,
) -> Dict[str, Any]:
    """
    Convenience wrapper for running a production simulation.
    """

    simulator = ProductionSimulator(
        scrap_cost_per_part=scrap_cost_per_part,
        rework_cost_per_part=rework_cost_per_part,
        downtime_cost_per_hour=downtime_cost_per_hour,
    )

    parameters = ProductionParameters(
        total_parts=total_parts,
        parts_per_hour=parts_per_hour,
        defect_rate=defect_rate,
        queue_time=queue_time,
        utilization=utilization,
        downtime_hours=downtime_hours,
        scrap_cost_per_part=scrap_cost_per_part,
        rework_cost_per_part=rework_cost_per_part,
        downtime_cost_per_hour=downtime_cost_per_hour,
    )

    return simulator.simulate(parameters)


# ----------------------------------------------------------------------
# Basic standalone test
# ----------------------------------------------------------------------

if __name__ == "__main__":

    result = run_production_simulation(
        total_parts=257155,
        parts_per_hour=209.45,
        defect_rate=0.043417,
        queue_time=2.4623,
        utilization=0.521,
        downtime_hours=0.041,
    )

    print("\nProduction Simulation")
    print("-" * 40)

    for key, value in result.items():
        print(f"{key}: {value}")