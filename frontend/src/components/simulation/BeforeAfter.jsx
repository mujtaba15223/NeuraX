import { ArrowRight, TrendingDown, TrendingUp } from "lucide-react";

function BeforeAfter({ before, after }) {
  if (!before || !after) {
    return (
      <div className="dashboard-card">
        <div className="card-header">
          <div>
            <span className="header-label">
              BEFORE / AFTER
            </span>

            <h3>Scenario Comparison</h3>
          </div>
        </div>

        <div className="empty-state">
          <p>
            Run a simulation to compare the current
            process with the projected scenario.
          </p>
        </div>
      </div>
    );
  }

  const formatNumber = (value) =>
    Number(value ?? 0).toLocaleString("en-IN", {
      maximumFractionDigits: 2,
    });

  const getChange = (beforeValue, afterValue) => {
    const beforeNumber = Number(beforeValue ?? 0);
    const afterNumber = Number(afterValue ?? 0);

    if (beforeNumber === 0) {
      return 0;
    }

    return (
      ((afterNumber - beforeNumber) /
        beforeNumber) *
      100
    );
  };

  const queueChange = getChange(
    before.queue,
    after.queue
  );

  const utilizationChange = getChange(
    before.utilization,
    after.utilization
  );

  const throughputChange = getChange(
    before.throughput,
    after.throughput
  );

  return (
    <div className="dashboard-card">
      <div className="card-header">
        <div>
          <span className="header-label">
            BEFORE / AFTER
          </span>

          <h3>Scenario Comparison</h3>
        </div>

        <ArrowRight size={22} />
      </div>

      <div className="dashboard-grid dashboard-grid-two">
        <div>
          <span className="header-label">
            CURRENT STATE
          </span>

          <div className="analysis-highlight">
            <span>Queue</span>
            <strong>
              {formatNumber(before.queue)}
            </strong>
          </div>

          <div className="analysis-highlight">
            <span>Utilization</span>
            <strong>
              {formatNumber(
                Number(before.utilization ?? 0) * 100
              )}
              %
            </strong>
          </div>

          <div className="analysis-highlight">
            <span>Throughput</span>
            <strong>
              {formatNumber(before.throughput)}
              / hr
            </strong>
          </div>
        </div>

        <div>
          <span className="header-label">
            PROJECTED STATE
          </span>

          <div className="analysis-highlight">
            <span>Queue</span>
            <strong>
              {formatNumber(after.queue)}
            </strong>

            <small
              style={{
                display: "flex",
                alignItems: "center",
                gap: "5px",
              }}
            >
              {queueChange <= 0 ? (
                <TrendingDown size={14} />
              ) : (
                <TrendingUp size={14} />
              )}

              {Math.abs(queueChange).toFixed(1)}%
            </small>
          </div>

          <div className="analysis-highlight">
            <span>Utilization</span>
            <strong>
              {formatNumber(
                Number(after.utilization ?? 0) * 100
              )}
              %
            </strong>

            <small>
              {utilizationChange >= 0 ? "+" : ""}
              {utilizationChange.toFixed(1)}%
            </small>
          </div>

          <div className="analysis-highlight">
            <span>Throughput</span>
            <strong>
              {formatNumber(after.throughput)}
              / hr
            </strong>

            <small>
              {throughputChange >= 0 ? "+" : ""}
              {throughputChange.toFixed(1)}%
            </small>
          </div>
        </div>
      </div>

      <small className="causality-note">
        Projected values represent a what-if scenario
        and should be validated before operational
        implementation.
      </small>
    </div>
  );
}

export default BeforeAfter;