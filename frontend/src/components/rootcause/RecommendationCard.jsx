import { Lightbulb, Wrench } from "lucide-react";

function RecommendationCard({ recommendation }) {
  if (!recommendation) {
    return (
      <div className="dashboard-card">
        <div className="card-header">
          <div>
            <span className="header-label">
              RECOMMENDATION
            </span>

            <h3>No Recommendation Available</h3>
          </div>

          <Lightbulb size={22} />
        </div>

        <div className="empty-state">
          <p>
            Recommendations will appear after the
            root-cause analysis is completed.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-card">
      <div className="card-header">
        <div>
          <span className="header-label">
            RECOMMENDATION
          </span>

          <h3>Recommended Investigation</h3>
        </div>

        <Wrench size={22} />
      </div>

      <div
        style={{
          padding: "18px",
          borderRadius: "10px",
          background: "#0b1118",
          border: "1px solid #263442",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "flex-start",
            gap: "12px",
          }}
        >
          <Lightbulb size={22} />

          <p
            style={{
              margin: 0,
              lineHeight: 1.7,
            }}
          >
            {recommendation}
          </p>
        </div>
      </div>

      <small className="causality-note">
        This recommendation identifies an
        investigation direction based on available
        process evidence. It is not a confirmed
        causal conclusion.
      </small>
    </div>
  );
}

export default RecommendationCard;