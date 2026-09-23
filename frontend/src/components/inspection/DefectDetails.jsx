import {
  AlertTriangle,
  CheckCircle2,
  Search,
  Factory,
  Target,
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

  const confidence =
    classificationConfidence == null
      ? null
      : Number(classificationConfidence);

  const similarity =
    prototypeSimilarity == null
      ? null
      : Number(prototypeSimilarity);

  const detectedDefect =
    defectType ||
    (isDefective
      ? "Visual anomaly detected"
      : "No defect detected");

  const formattedDefect = detectedDefect
    .replace(/_/g, " ")
    .replace(/\b\w/g, (char) =>
      char.toUpperCase()
    );

  const sortedClassScores = Object.entries(
    classScores || {}
  ).sort(([, a], [, b]) => Number(b) - Number(a));

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

      {/* Main classification */}
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
              {formattedDefect}
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
              {limit.toFixed(4)}
            </strong>
          </div>
        </div>

        {isDefective && (
          <div className="detail-item">
            <div className="detail-icon">
              <Target size={20} />
            </div>

            <div>
              <span>Classification Confidence</span>

              <strong>
                {confidence == null
                  ? "Not available"
                  : `${(
                      confidence * 100
                    ).toFixed(1)}%`}
              </strong>
            </div>
          </div>
        )}
      </div>

      {/* Prototype evidence */}
      {isDefective &&
        sortedClassScores.length > 0 && (
          <div className="defect-investigation">
            <span className="header-label">
              DEFECT CLASSIFICATION EVIDENCE
            </span>

            <h4>
              Prototype Similarity
            </h4>

            <div className="impact-list">
              {sortedClassScores.map(
                ([label, value]) => (
                  <div key={label}>
                    <span>
                      {label
                        .replace(/_/g, " ")
                        .replace(
                          /\b\w/g,
                          (char) =>
                            char.toUpperCase()
                        )}
                    </span>

                    <strong>
                      {Number(value).toFixed(4)}
                    </strong>
                  </div>
                )
              )}
            </div>

            {similarity != null && (
              <p className="analysis-text">
                <strong>
                  Prototype similarity:
                </strong>{" "}
                {similarity.toFixed(4)}
              </p>
            )}

            <small className="causality-note">
              These scores indicate similarity to
              stored defect prototypes. They are
              diagnostic evidence and should not be
              interpreted as independently validated
              supervised classification probabilities.
            </small>
          </div>
        )}

      {/* Process investigation */}
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

      {/* Causality warning */}
      <small className="causality-note">
        Visual inspection identifies visual deviation.
        It does not independently establish a
        manufacturing root cause. Process evidence is
        required to identify likely contributing factors.
      </small>
    </div>
  );
}

export default DefectDetails;