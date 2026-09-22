import { useEffect, useState } from "react";
import { RefreshCw, Play, AlertTriangle } from "lucide-react";

import ScenarioControls from "../components/simulation/ScenarioControls";
import SimulationResults from "../components/simulation/SimulationResults";
import BeforeAfter from "../components/simulation/BeforeAfter";
import ImpactComparison from "../components/simulation/ImpactComparison";
import API_BASE_URL from "../config/api";

function Simulation() {
  const [analysis, setAnalysis] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState("");

  const fetchAnalysis = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await fetch(
        `${API_BASE_URL}/analysis`
      );

      if (!response.ok) {
        throw new Error(
          "Failed to load production analysis"
        );
      }

      const data = await response.json();

      setAnalysis(data);
    } catch (err) {
      setError(
        err.message ||
          "Unable to connect to backend"
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalysis();
  }, []);

  const runSimulation = async ({
    station,
    scenario,
    improvement,
  }) => {
    if (!analysis) {
      return;
    }

    setRunning(true);
    setError("");
    setResult(null);

    try {
      /*
       * The ScenarioControls component uses human-readable
       * scenario names. Convert them to the scenario IDs
       * understood by the Python simulation engine.
       */

      const scenarioMap = {
        "Reduce Queue Time": "reduce_queue",
        "Increase Capacity": "increase_capacity",
        "Reduce Utilization": "reduce_queue",
        "Reduce Cycle Time": "increase_capacity",
        "Reduce Defects": "reduce_defects",
        "Process Optimization":
          "process_optimization",
        "Preventive Maintenance":
          "maintenance",
        "Quality + Flow Improvement":
          "quality_and_flow",
      };

      const scenarioId =
        scenarioMap[scenario] ||
        "process_optimization";

      /*
       * Send the scenario to the real backend.
       */

      const response = await fetch(
        `${API_BASE_URL}/simulation`,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
            mode: "scenario",
            scenario: scenarioId,
          }),
        }
      );

      if (!response.ok) {
        let message =
          "Simulation request failed";

        try {
          const errorData =
            await response.json();

          message =
            errorData?.detail ||
            errorData?.message ||
            message;
        } catch {
          // Keep default message.
        }

        throw new Error(message);
      }

      const data = await response.json();

      /*
       * Backend returns:
       *
       * baseline
       * simulated
       * comparison
       * interpretation
       */

      if (
        data.status !== "success" &&
        data.status !== "simulation_complete"
      ) {
        throw new Error(
          data.message ||
            "Simulation could not be completed"
        );
      }

      const baseline =
        data.baseline || {};

      const simulated =
        data.simulated ||
        data.scenario ||
        {};

      /*
       * Normalize the backend response into the
       * structure expected by the existing UI components.
       */

      const normalizedResult = {
        station,

        scenario:
          data.scenario?.name ||
          scenario,

        scenarioId:
          data.scenario?.id ||
          scenarioId,

        improvement:
          Number(improvement) || 0,

        before: {
          queue:
            Number(
              baseline.queue_time
            ) || 0,

          utilization:
            Number(
              baseline.utilization
            ) || 0,

          throughput:
            Number(
              baseline.effective_throughput ??
                baseline.parts_per_hour
            ) || 0,
        },

        after: {
          queue:
            Number(
              simulated.queue_time
            ) || 0,

          utilization:
            Number(
              simulated.utilization
            ) || 0,

          throughput:
            Number(
              simulated.effective_throughput ??
                simulated.parts_per_hour
            ) || 0,
        },

        baseline: {
          throughput:
            Number(
              baseline.effective_throughput ??
                baseline.parts_per_hour
            ) || 0,

          queue:
            Number(
              baseline.queue_time
            ) || 0,

          impact:
            Number(
              baseline.estimated_economic_impact
            ) || 0,

          defectRate:
            Number(
              baseline.defect_rate
            ) || 0,

          defectiveParts:
            Number(
              baseline.defective_parts
            ) || 0,
        },

        simulated: {
          throughput:
            Number(
              simulated.effective_throughput ??
                simulated.parts_per_hour
            ) || 0,

          queue:
            Number(
              simulated.queue_time
            ) || 0,

          impact:
            Number(
              simulated.estimated_economic_impact
            ) || 0,

          defectRate:
            Number(
              simulated.defect_rate
            ) || 0,

          defectiveParts:
            Number(
              simulated.defective_parts
            ) || 0,
        },

        estimated_savings:
          Math.max(
            0,
            Number(
              baseline.estimated_economic_impact
            ) -
              Number(
                simulated.estimated_economic_impact
              )
          ),

        comparison:
          data.comparison || null,

        interpretation:
          data.interpretation || null,

        decisionSupportNote:
          data.decision_support_note ||
          "Simulation results are estimates based on configurable assumptions.",
      };

      setResult(normalizedResult);
    } catch (err) {
      setError(
        err.message ||
          "Unable to run simulation"
      );
    } finally {
      setRunning(false);
    }
  };

  if (loading) {
    return (
      <div className="page-container">
        <div className="page-header">
          <div>
            <span className="header-label">
              WHAT-IF SIMULATION
            </span>

            <h1>
              Production Simulation
            </h1>

            <p>
              Test process improvements before
              applying them to production.
            </p>
          </div>
        </div>

        <div className="dashboard-card">
          <div className="empty-state">
            <RefreshCw
              className="spin"
              size={28}
            />

            <p>
              Loading production model...
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (error && !analysis) {
    return (
      <div className="page-container">
        <div className="page-header">
          <div>
            <span className="header-label">
              WHAT-IF SIMULATION
            </span>

            <h1>
              Production Simulation
            </h1>

            <p>
              Test process improvements before
              applying them to production.
            </p>
          </div>
        </div>

        <div className="dashboard-card">
          <div className="empty-state">
            <AlertTriangle size={30} />

            <h3>
              Simulation Unavailable
            </h3>

            <p>{error}</p>

            <button
              className="action-button"
              onClick={fetchAnalysis}
            >
              <RefreshCw size={16} />
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <span className="header-label">
            WHAT-IF SIMULATION
          </span>

          <h1>
            Production Simulation
          </h1>

          <p>
            Test process improvements and estimate
            their effect on throughput, queue
            pressure, quality, and economic impact.
          </p>
        </div>

        <button
          className="action-button"
          onClick={fetchAnalysis}
          disabled={running}
        >
          <RefreshCw size={16} />
          Refresh Model
        </button>
      </div>

      {error && (
        <div className="dashboard-card">
          <div className="empty-state">
            <AlertTriangle size={24} />

            <p>{error}</p>
          </div>
        </div>
      )}

      <div className="dashboard-card">
        <div className="card-header">
          <div>
            <span className="header-label">
              SCENARIO BUILDER
            </span>

            <h3>
              Configure What-If Scenario
            </h3>
          </div>

          <Play size={22} />
        </div>

        <ScenarioControls
          onRun={runSimulation}
          running={running}
        />

        {running && (
          <div className="simulation-running">
            <RefreshCw
              className="spin"
              size={18}
            />

            Running Python simulation...
          </div>
        )}
      </div>

      <SimulationResults
        result={result}
      />

      {result && (
        <>
          <BeforeAfter
            before={result.before}
            after={result.after}
          />

          <ImpactComparison
            baseline={result.baseline}
            simulated={result.simulated}
          />

          <div className="dashboard-card">
            <div className="card-header">
              <div>
                <span className="header-label">
                  SIMULATION OUTPUT
                </span>

                <h3>
                  Decision Support Summary
                </h3>
              </div>
            </div>

            <div className="simulation-summary">
              <p>
                <strong>
                  Scenario:
                </strong>{" "}
                {result.scenario}
              </p>

              <p>
                <strong>
                  Estimated defective parts:
                </strong>{" "}
                {result.baseline.defectiveParts.toLocaleString()}{" "}
                →{" "}
                {result.simulated.defectiveParts.toLocaleString()}
              </p>

              <p>
                <strong>
                  Estimated economic impact:
                </strong>{" "}
                ₹
                {result.baseline.impact.toLocaleString(
                  "en-IN",
                  {
                    maximumFractionDigits: 2,
                  }
                )}{" "}
                → ₹
                {result.simulated.impact.toLocaleString(
                  "en-IN",
                  {
                    maximumFractionDigits: 2,
                  }
                )}
              </p>

              <p>
                <strong>
                  Estimated impact reduction:
                </strong>{" "}
                ₹
                {result.estimated_savings.toLocaleString(
                  "en-IN",
                  {
                    maximumFractionDigits: 2,
                  }
                )}
              </p>
            </div>
          </div>
        </>
      )}

      <div className="dashboard-card causality-warning">
        <div className="warning-icon">
          <AlertTriangle size={20} />
        </div>

        <div>
          <strong>
            Simulation Assumption
          </strong>

          <p>
            What-if results are modeled estimates
            based on configurable improvement
            assumptions. They should be validated
            with real production experiments before
            operational decisions are made.
          </p>
        </div>
      </div>
    </div>
  );
}

export default Simulation;