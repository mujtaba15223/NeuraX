import {
  AlertTriangle,
  CheckCircle2,
  Search,
  Factory,
} from "lucide-react";

function DefectDetails({
  status,
  anomalyScore,
  threshold,
  defectType,
  classificationConfidence,
  prototypeSimilarity,
  classScores,
  likelyCause,
}) {
  const isDefective =
    status?.toLowerCase() === "defective";

  const score = Number(anomalyScore ?? 0);
  const limit = Number(threshold ?? 0);

  const detectedDefect =
    defectType ||
    (isDefective
      ? "Visual anomaly detected"
      : "No defect detected");

  return (
    <div className="dashboard-card">
      <div className="card-header">
        <div>
          <span className="header-label">
            DEFECT DETAILS
          </span>

          <h3>Inspection Findings</h3>
        </div>

        <Search size={22} />
      </div>

      <div className="defect-details-grid">
        <div className="detail-item">
          <div className="detail-icon">
            {isDefective ? (
              <AlertTriangle size={20} />
            ) : (
              <CheckCircle2 size={20} />
            )}
          </div>

          <div>
            <span>Classification</span>
            <strong>
              {detectedDefect}
            </strong>
          </div>
        </div>

        <div className="detail-item">
          <div className="detail-icon">
            <Search size={20} />
          </div>

          <div>
            <span>Anomaly Score</span>
            <strong>
              {score.toFixed(4)}
            </strong>
          </div>
        </div>

        <div className="detail-item">
          <div className="detail-icon">
            <Factory size={20} />
          </div>

          <div>
            <span>Inspection Threshold</span>
            <strong>

        {isDefective && defectType && (
          <div className="detail-item">
            <div className="detail-icon">
              <Search size={20} />
            </div>

            <div>
              <span>Classification Confidence</span>
              <strong>
                {classificationConfidence == null
                  ? "Not available"
                  : `${(
                      Number(classificationConfidence) * 100
                    ).toFixed(1)}%`}
              </strong>
            </div>
          </div>
        )}
              {limit.toFixed(2)}

      {isDefective && Object.keys(classScores || {}).length > 0 && (
        <div className="defect-investigation">
          <span className="header-label">
            PROTOTYPE CLASS SCORES
          </span>

          <div className="impact-list">
            {Object.entries(classScores).map(
              ([label, value]) => (
                <div key={label}>
                  <span>{label}</span>
                  <strong>{Number(value).toFixed(4)}</strong>
                </div>
              )
            )}
          </div>

          <small className="causality-note">
            Classification uses similarity to stored defect prototypes; it
            is an investigation aid, not a supervised defect classifier.
            Prototype similarity: {Number(prototypeSimilarity ?? 0).toFixed(4)}
          </small>
        </div>
      )}
            </strong>
          </div>
        </div>
      </div>

      <div className="defect-investigation">
        <span className="header-label">
          INVESTIGATION DIRECTION
        </span>

        <h4>
          {isDefective
            ? "Further Process Investigation Recommended"
            : "No Immediate Process Investigation Required"}
        </h4>

        <p>
          {likelyCause ||
            (isDefective
              ? "The visual anomaly should be correlated with process conditions, queue behavior, utilization, and production events to identify likely contributing factors."
              : "The inspected image does not currently provide sufficient visual evidence to trigger a defect investigation.")}
        </p>
      </div>

      <small className="causality-note">
        Visual inspection identifies an anomaly but does
        not independently establish its manufacturing
        cause. Process evidence is required for
        root-cause investigation.
      </small>
    </div>
  );
}

export default DefectDetails;