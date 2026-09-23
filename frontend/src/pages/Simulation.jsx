import { useEffect, useState } from "react";
import {
  RefreshCw,
  Play,
  AlertTriangle,
  FlaskConical,
  TrendingUp,
  TrendingDown,
  IndianRupee,
  Gauge,
  ShieldCheck,
} from "lucide-react";

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

  const formatNumber = (value) =>
    Number(value ?? 0).toLocaleString(
      "en-IN",
      {
        maximumFractionDigits: 2,
      }
    );

  const formatCurrency = (value) =>
    `₹${Number(value ?? 0).toLocaleString(
      "en-IN",
      {
        maximumFractionDigits: 0,
      }
    )}`;

  const calculateChange = (
    before,
    after
  ) => {
    if (!before) {
      return 0;
    }

    return (
      ((after - before) / before) *
      100
    );
  };

  if (loading) {
    return (
      <main className="page-container">
        <section className="page-header">
          <div>
            <span className="header-label">
              WHAT-IF SIMULATION
            </span>

            <h1>
              Production Simulation
            </h1>

            <p>
              Loading the production decision
              model and simulation engine.
            </p>
          </div>
        </section>

        <section className="dashboard-card">
          <div className="empty-state">
            <RefreshCw
              className="spin"
              size={30}
            />

            <h3>
              Loading production model...
            </h3>

            <p>
              Preparing the what-if simulation
              environment.
            </p>
          </div>
        </section>
      </main>
    );
  }

  if (error && !analysis) {
    return (
      <main className="page-container">
        <section className="page-header">
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
        </section>

        <section className="dashboard-card">
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
        </section>
      </main>
    );
  }

  return (
    <main className="page-container">

      {/* HEADER */}
      <section className="page-header">
        <div>
          <span className="header-label">
            WHAT-IF SIMULATION
          </span>

          <h1>
            Production Simulation
          </h1>

          <p>
            Test process improvements and
            estimate their effect on throughput,
            quality, queue pressure, and
            economic impact.
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
      </section>

      {/* MODEL STATUS */}
      <section className="dashboard-grid">

        <div className="dashboard-card">
          <div className="card-header">
            <div>
              <span className="header-label">
                SIMULATION ENGINE
              </span>

              <h3>
                Model Ready
              </h3>
            </div>

            <ShieldCheck size={22} />
          </div>

          <div className="station-score">
            <span>
              Backend Status
            </span>

            <strong>
              READY
            </strong>
          </div>

          <small>
            Production model loaded and
            available for what-if analysis.
          </small>
        </div>

        <div className="dashboard-card">
          <div className="card-header">
            <div>
              <span className="header-label">
                DECISION SUPPORT
              </span>

              <h3>
                Scenario Testing
              </h3>
            </div>

            <FlaskConical size={22} />
          </div>

          <div className="station-score">
            <span>
              Mode
            </span>

            <strong>
              WHAT-IF
            </strong>
          </div>

          <small>
            Compare modeled baseline and
            improved production states.
          </small>
        </div>

        <div className="dashboard-card">
          <div className="card-header">
            <div>
              <span className="header-label">
                OUTPUTS
              </span>

              <h3>
                Impact Metrics
              </h3>
            </div>

            <Gauge size={22} />
          </div>

          <div className="metric-row">
            <span>
              Throughput
            </span>

            <strong>
              ✓
            </strong>
          </div>

          <div className="metric-row">
            <span>
              Queue
            </span>

            <strong>
              ✓
            </strong>
          </div>

          <div className="metric-row">
            <span>
              Economics
            </span>

            <strong>
              ✓
            </strong>
          </div>
        </div>

      </section>

      {/* ERROR DURING SIMULATION */}
      {error && (
        <section className="dashboard-card">
          <div className="empty-state">
            <AlertTriangle size={24} />

            <p>{error}</p>
          </div>
        </section>
      )}

      {/* SCENARIO BUILDER */}
      <section className="dashboard-card">
        <div className="card-header">
          <div>
            <span className="header-label">
              SCENARIO BUILDER
            </span>

            <h3>
              Configure What-If Scenario
            </h3>

            <p>
              Select a process improvement and
              run it through the production
              simulation engine.
            </p>
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
      </section>

      {/* RESULTS */}
      {result && (
        <>
          {/* RESULT HERO */}
          <section className="dashboard-card bottleneck-highlight">

            <div className="highlight-icon">
              <TrendingUp size={28} />
            </div>

            <div>
              <span className="header-label">
                SIMULATION COMPLETE
              </span>

              <h2>
                {result.scenario}
              </h2>

              <p>
                Modeled comparison between the
                current production baseline and
                the selected improvement scenario.
              </p>
            </div>

            <div className="highlight-score">
              <span>
                Estimated Savings
              </span>

              <strong>
                {formatCurrency(
                  result.estimated_savings
                )}
              </strong>

              <small>
                Modeled economic reduction
              </small>
            </div>

          </section>

          {/* QUICK COMPARISON */}
          <section className="dashboard-grid">

            <div className="dashboard-card">
              <div className="card-header">
                <div>
                  <span className="header-label">
                    THROUGHPUT
                  </span>

                  <h3>
                    Production Rate
                  </h3>
                </div>

                <TrendingUp size={22} />
              </div>

              <div className="station-score">
                <span>
                  Before
                </span>

                <strong>
                  {formatNumber(
                    result.baseline.throughput
                  )}
                </strong>
              </div>

              <div className="metric-row">
                <span>
                  After
                </span>

                <strong>
                  {formatNumber(
                    result.simulated.throughput
                  )}
                </strong>
              </div>

              <div className="metric-row">
                <span>
                  Change
                </span>

                <strong>
                  {calculateChange(
                    result.baseline.throughput,
                    result.simulated.throughput
                  ).toFixed(2)}
                  %
                </strong>
              </div>
            </div>

            <div className="dashboard-card">
              <div className="card-header">
                <div>
                  <span className="header-label">
                    QUEUE PRESSURE
                  </span>

                  <h3>
                    Process Queue
                  </h3>
                </div>

                <TrendingDown size={22} />
              </div>

              <div className="station-score">
                <span>
                  Before
                </span>

                <strong>
                  {formatNumber(
                    result.baseline.queue
                  )}
                </strong>
              </div>

              <div className="metric-row">
                <span>
                  After
                </span>

                <strong>
                  {formatNumber(
                    result.simulated.queue
                  )}
                </strong>
              </div>

              <div className="metric-row">
                <span>
                  Change
                </span>

                <strong>
                  {calculateChange(
                    result.baseline.queue,
                    result.simulated.queue
                  ).toFixed(2)}
                  %
                </strong>
              </div>
            </div>

            <div className="dashboard-card">
              <div className="card-header">
                <div>
                  <span className="header-label">
                    QUALITY
                  </span>

                  <h3>
                    Defective Parts
                  </h3>
                </div>

                <ShieldCheck size={22} />
              </div>

              <div className="station-score">
                <span>
                  Before
                </span>

                <strong>
                  {formatNumber(
                    result.baseline.defectiveParts
                  )}
                </strong>
              </div>

              <div className="metric-row">
                <span>
                  After
                </span>

                <strong>
                  {formatNumber(
                    result.simulated.defectiveParts
                  )}
                </strong>
              </div>

              <div className="metric-row">
                <span>
                  Defect Rate
                </span>

                <strong>
                  {(
                    result.simulated.defectRate *
                    100
                  ).toFixed(2)}
                  %
                </strong>
              </div>
            </div>

            <div className="dashboard-card">
              <div className="card-header">
                <div>
                  <span className="header-label">
                    ECONOMICS
                  </span>

                  <h3>
                    Estimated Impact
                  </h3>
                </div>

                <IndianRupee size={22} />
              </div>

              <div className="station-score">
                <span>
                  Before
                </span>

                <strong>
                  {formatCurrency(
                    result.baseline.impact
                  )}
                </strong>
              </div>

              <div className="metric-row">
                <span>
                  After
                </span>

                <strong>
                  {formatCurrency(
                    result.simulated.impact
                  )}
                </strong>
              </div>

              <div className="metric-row">
                <span>
                  Estimated Reduction
                </span>

                <strong>
                  {formatCurrency(
                    result.estimated_savings
                  )}
                </strong>
              </div>
            </div>

          </section>

          {/* EXISTING COMPONENTS */}
          <SimulationResults
            result={result}
          />

          <BeforeAfter
            before={result.before}
            after={result.after}
          />

          <ImpactComparison
            baseline={result.baseline}
            simulated={result.simulated}
          />

          {/* DECISION SUPPORT */}
          <section className="dashboard-card">

            <div className="card-header">
              <div>
                <span className="header-label">
                  SIMULATION OUTPUT
                </span>

                <h3>
                  Decision Support Summary
                </h3>
              </div>

              <FlaskConical size={22} />
            </div>

            <div className="simulation-summary">

              <div className="summary-row">
                <span>
                  Scenario
                </span>

                <strong>
                  {result.scenario}
                </strong>
              </div>

              <div className="summary-row">
                <span>
                  Estimated Defective Parts
                </span>

                <strong>
                  {formatNumber(
                    result.baseline.defectiveParts
                  )}
                  {" → "}
                  {formatNumber(
                    result.simulated.defectiveParts
                  )}
                </strong>
              </div>

              <div className="summary-row">
                <span>
                  Estimated Economic Impact
                </span>

                <strong>
                  {formatCurrency(
                    result.baseline.impact
                  )}
                  {" → "}
                  {formatCurrency(
                    result.simulated.impact
                  )}
                </strong>
              </div>

              <div className="summary-row">
                <span>
                  Estimated Impact Reduction
                </span>

                <strong>
                  {formatCurrency(
                    result.estimated_savings
                  )}
                </strong>
              </div>

            </div>

            {result.interpretation && (
              <div className="simulation-interpretation">
                <span className="header-label">
                  MODEL INTERPRETATION
                </span>

                <p>
                  {typeof result.interpretation ===
                  "string"
                    ? result.interpretation
                    : JSON.stringify(
                        result.interpretation
                      )}
                </p>
              </div>
            )}

            {result.decisionSupportNote && (
              <small className="causality-note">
                {result.decisionSupportNote}
              </small>
            )}

          </section>
        </>
      )}

      {/* MODEL LIMITATION */}
      <section className="dashboard-card causality-warning">

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
            assumptions. They represent decision
            support rather than guaranteed production
            outcomes. Real production trials and
            validated operational data should be
            used before implementing process changes.
          </p>
        </div>

      </section>

    </main>
  );
}

export default Simulation;