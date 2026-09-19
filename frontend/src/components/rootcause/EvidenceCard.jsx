import { Activity, Clock, Gauge } from "lucide-react";

function EvidenceCard({ evidence }) {
  if (!evidence) {
    return (
      <div className="dashboard-card">
        <div className="card-header">
          <div>
            <span className="header-label">
              PROCESS EVIDENCE
            </span>
            <h3>No Evidence Available</h3>
          </div>

          <Activity size={22} />
        </div>

        <div className="empty-state">
          <p>
            Process evidence will appear when analysis
            data is available.
          </p>
        </div>
      </div>
    );
  }

  const formatNumber = (value) =>
    Number(value ?? 0).toFixed(4);

  return (
    <div className="dashboard-card">
      <div className="card-header">
        <div>
          <span className="header-label">
            PROCESS EVIDENCE
          </span>

          <h3>Supporting Signals</h3>
        </div>

        <Activity size={22} />
      </div>

      <div className="dashboard-grid">
        <div className="analysis-highlight">
          <span>
            <Clock size={14} /> Average Queue
          </span>

          <strong>
            {formatNumber(
              evidence.average_queue
            )}
          </strong>
        </div>

        <div className="analysis-highlight">
          <span>
            <Gauge size={14} /> Average Utilization
          </span>

          <strong>
            {(
              Number(
                evidence.average_utilization ?? 0
              ) * 100
            ).toFixed(1)}
            %
          </strong>
        </div>

        <div className="analysis-highlight">
          <span>Pressure Score</span>

          <strong>
            {formatNumber(
              evidence.pressure_score
            )}
          </strong>
        </div>
      </div>

      <small className="causality-note">
        These measurements provide process evidence
        for investigation; they do not establish
        causality by themselves.
      </small>
    </div>
  );
}

export default EvidenceCard;