import { Brain, GitBranch } from "lucide-react";

function RootCausePanel({ data }) {
  if (!data) {
    return (
      <div className="dashboard-card">
        <div className="card-header">
          <div>
            <span className="header-label">
              ROOT-CAUSE ASSISTANT
            </span>

            <h3>Awaiting Analysis</h3>
          </div>

          <Brain size={22} />
        </div>

        <div className="empty-state">
          <p>
            Root-cause evidence will appear after the
            production and inspection analysis is
            available.
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
            ROOT-CAUSE ASSISTANT
          </span>

          <h3>Investigation Summary</h3>
        </div>

        <GitBranch size={22} />
      </div>

      <div className="dashboard-grid dashboard-grid-two">
        <div className="analysis-highlight">
          <span>Detected Defect</span>

          <strong>
            {data.defect || "N/A"}
          </strong>
        </div>

        <div className="analysis-highlight">
          <span>
            Likely Contributing Factor
          </span>

          <strong>
            {data.likely_contributing_factor ||
              "N/A"}
          </strong>
        </div>
      </div>

      <div
        style={{
          marginTop: "18px",
          padding: "16px",
          borderRadius: "10px",
          background: "#0b1118",
          border: "1px solid #263442",
        }}
      >
        <span className="header-label">
          INVESTIGATION REASONING
        </span>

        <p
          style={{
            marginTop: "8px",
            lineHeight: 1.6,
          }}
        >
          {data.reasoning ||
            "Process evidence indicates a potential contributing factor that should be investigated further."}
        </p>
      </div>

      <small className="causality-note">
        {data.causality_note ||
          "This is process evidence and an investigation hypothesis, not proof of causality."}
      </small>
    </div>
  );
}

export default RootCausePanel;