import {
  CheckCircle2,
  AlertTriangle,
  Activity,
} from "lucide-react";

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

  const margin = score - limit;

  const marginPercent =
    limit > 0
      ? (margin / limit) * 100
      : 0;

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
              ? "The visual anomaly score is above the configured inspection threshold."
              : "The visual anomaly score is below the configured inspection threshold."}
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
          <span>Decision Threshold</span>

          <strong>
            {limit.toFixed(4)}
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

        <div className="inspection-metric">
          <span>Score Margin</span>

          <strong>
            {margin >= 0 ? "+" : ""}
            {margin.toFixed(4)}
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

      <div className="inspection-interpretation">
        <span className="header-label">
          DECISION INTERPRETATION
        </span>

        <p>
          {isDefective ? (
            <>
              The anomaly score is{" "}
              <strong>
                {Math.abs(marginPercent).toFixed(1)}%
              </strong>{" "}
              above the configured threshold. The
              image should proceed to defect
              classification and process-level
              investigation.
            </>
          ) : (
            <>
              The anomaly score is{" "}
              <strong>
                {Math.abs(marginPercent).toFixed(1)}%
              </strong>{" "}
              below the configured threshold. The
              image is classified as visually normal
              by the current detection model.
            </>
          )}
        </p>
      </div>

      <small className="causality-note">
        The anomaly detector identifies visual
        deviation from the normal reference feature
        database. It does not by itself establish a
        manufacturing root cause. Process evidence is
        required for root-cause investigation.
      </small>
    </div>
  );
}

export default DefectResult;