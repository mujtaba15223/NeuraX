import { Activity, CheckCircle } from "lucide-react";

function SimulationResults({ result }) {
  if (!result) {
    return (
      <div className="dashboard-card">
        <div className="card-header">
          <div>
            <span className="header-label">
              SIMULATION RESULTS
            </span>

            <h3>Awaiting Scenario</h3>
          </div>

          <Activity size={22} />
        </div>

        <div className="empty-state">
          <p>
            Configure a scenario and run the simulation
            to see the projected production impact.
          </p>
        </div>
      </div>
    );
  }

  const formatNumber = (value) =>
    Number(value ?? 0).toLocaleString("en-IN", {
      maximumFractionDigits: 2,
    });

  const formatPercent = (value) =>
    `${Number(value ?? 0).toFixed(1)}%`;

  return (
    <div className="dashboard-card">
      <div className="card-header">
        <div>
          <span className="header-label">
            SIMULATION RESULTS
          </span>

          <h3>Projected Outcome</h3>
        </div>

        <CheckCircle size={22} />
      </div>

      <div className="dashboard-grid">
        <div className="analysis-highlight">
          <span>Station</span>
          <strong>{result.station || "N/A"}</strong>
        </div>

        <div className="analysis-highlight">
          <span>Scenario</span>
          <strong>{result.scenario || "N/A"}</strong>
        </div>

        <div className="analysis-highlight">
          <span>Improvement</span>
          <strong>
            {formatPercent(result.improvement)}
          </strong>
        </div>

        <div className="analysis-highlight">
          <span>Projected Queue</span>
          <strong>
            {formatNumber(result.after?.queue ?? result.projected_queue ?? 0)}
          </strong>
        </div>

        <div className="analysis-highlight">
          <span>Projected Utilization</span>
          <strong>
            {formatPercent(
              Number(result.after?.utilization ?? result.projected_utilization ?? 0) * 100
            )}
          </strong>
        </div>

        <div className="analysis-highlight">
          <span>Projected Throughput</span>
          <strong>
            {formatNumber(
              result.after?.throughput ?? result.projected_throughput ?? 0
            )}
            / hr
          </strong>
        </div>
      </div>

      <small className="causality-note">
        Simulation results are scenario estimates based
        on configurable assumptions, not guaranteed
        production outcomes.
      </small>
    </div>
  );
}

export default SimulationResults;