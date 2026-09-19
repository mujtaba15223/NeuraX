import { CheckCircle2, AlertTriangle, Activity } from "lucide-react";

function DefectResult({
  status,
  anomalyScore,
  threshold,
  model,
}) {
  const isDefective =
    status?.toLowerCase() === "defective";

  const score = Number(anomalyScore ?? 0);
  const limit = Number(threshold ?? 0);

  return (
    <div className="dashboard-card">
      <div className="card-header">
        <div>
          <span className="header-label">
            AI INSPECTION RESULT
          </span>

          <h3>Defect Classification</h3>
        </div>

        <Activity size={22} />
      </div>

      <div
        className={`inspection-result ${
          isDefective
            ? "result-defective"
            : "result-good"
        }`}
      >
        <div className="result-icon">
          {isDefective ? (
            <AlertTriangle size={34} />
          ) : (
            <CheckCircle2 size={34} />
          )}
        </div>

        <div>
          <span className="result-label">
            INSPECTION STATUS
          </span>

          <h2>
            {status ||
              (isDefective
                ? "DEFECTIVE"
                : "GOOD")}
          </h2>

          <p>
            {isDefective
              ? "The AI detected an anomaly above the configured inspection threshold."
              : "No significant visual anomaly was detected above the configured threshold."}
          </p>
        </div>
      </div>

      <div className="inspection-metrics">
        <div className="inspection-metric">
          <span>Anomaly Score</span>
          <strong>
            {score.toFixed(4)}
          </strong>
        </div>

        <div className="inspection-metric">
          <span>Threshold</span>
          <strong>
            {limit.toFixed(2)}
          </strong>
        </div>

        <div className="inspection-metric">
          <span>Decision</span>
          <strong>
            {isDefective
              ? "ANOMALY"
              : "NORMAL"}
          </strong>
        </div>
      </div>

      <div className="model-info">
        <span>Detection Model</span>

        <strong>
          {model ||
            "ResNet18 feature anomaly detector"}
        </strong>
      </div>

      <small className="causality-note">
        The anomaly score indicates visual similarity
        to the normal reference feature database. It
        does not by itself identify the manufacturing
        root cause.
      </small>
    </div>
  );
}

export default DefectResult;