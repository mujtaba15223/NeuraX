import {
  ArrowDown,
  ArrowUp,
  IndianRupee,
  TrendingUp,
} from "lucide-react";

function ImpactComparison({ baseline, simulated }) {
  if (!baseline || !simulated) {
    return (
      <div className="dashboard-card">
        <div className="card-header">
          <div>
            <span className="header-label">
              IMPACT COMPARISON
            </span>

            <h3>Production Impact</h3>
          </div>

          <IndianRupee size={22} />
        </div>

        <div className="empty-state">
          <p>
            Run a simulation to see the projected
            operational and economic impact.
          </p>
        </div>
      </div>
    );
  }

  const formatCurrency = (value) =>
    `₹${Number(value ?? 0).toLocaleString("en-IN", {
      maximumFractionDigits: 0,
    })}`;

  const formatNumber = (value) =>
    Number(value ?? 0).toLocaleString("en-IN", {
      maximumFractionDigits: 2,
    });

  const calculateChange = (
    baselineValue,
    simulatedValue
  ) => {
    const base = Number(baselineValue ?? 0);
    const after = Number(simulatedValue ?? 0);

    if (base === 0) {
      return 0;
    }

    return ((after - base) / base) * 100;
  };

  const throughputChange = calculateChange(
    baseline.throughput,
    simulated.throughput
  );

  const queueChange = calculateChange(
    baseline.queue,
    simulated.queue
  );

  const impactChange = calculateChange(
    baseline.economic_impact,
    simulated.economic_impact
  );

  return (
    <div className="dashboard-card">
      <div className="card-header">
        <div>
          <span className="header-label">
            IMPACT COMPARISON
          </span>

          <h3>Projected Production Impact</h3>
        </div>

        <TrendingUp size={22} />
      </div>

      <div className="dashboard-grid">
        <div className="analysis-highlight">
          <span>Throughput Change</span>

          <strong>
            {throughputChange >= 0 ? "+" : ""}
            {throughputChange.toFixed(1)}%
          </strong>

          <small>
            {formatNumber(simulated.throughput)}
            {" / hr"}
          </small>
        </div>

        <div className="analysis-highlight">
          <span>Queue Change</span>

          <strong
            style={{
              display: "flex",
              alignItems: "center",
              gap: "6px",
            }}
          >
            {queueChange <= 0 ? (
              <ArrowDown size={16} />
            ) : (
              <ArrowUp size={16} />
            )}

            {Math.abs(queueChange).toFixed(1)}%
          </strong>

          <small>
            {formatNumber(simulated.queue)}
          </small>
        </div>

        <div className="analysis-highlight">
          <span>Baseline Impact</span>

          <strong>
            {formatCurrency(
              baseline.economic_impact
            )}
          </strong>
        </div>

        <div className="analysis-highlight">
          <span>Projected Impact</span>

          <strong>
            {formatCurrency(
              simulated.economic_impact
            )}
          </strong>
        </div>

        <div className="analysis-highlight">
          <span>Estimated Savings</span>

          <strong>
            {formatCurrency(
              Number(
                baseline.economic_impact ?? 0
              ) -
                Number(
                  simulated.economic_impact ?? 0
                )
            )}
          </strong>
        </div>
      </div>

      <small className="causality-note">
        Economic impact is based on configurable
        demonstration assumptions. Simulation results
        are projections, not guaranteed savings.
      </small>
    </div>
  );
}

export default ImpactComparison;