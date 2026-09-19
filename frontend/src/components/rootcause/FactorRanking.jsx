import { BarChart3, TrendingUp } from "lucide-react";

function FactorRanking({ factors }) {
  if (!factors || factors.length === 0) {
    return (
      <div className="dashboard-card">
        <div className="card-header">
          <div>
            <span className="header-label">
              FACTOR RANKING
            </span>

            <h3>No Factors Available</h3>
          </div>

          <BarChart3 size={22} />
        </div>

        <div className="empty-state">
          <p>
            Potential contributing factors will appear
            after process analysis.
          </p>
        </div>
      </div>
    );
  }

  const formatScore = (value) =>
    Number(value ?? 0).toFixed(4);

  return (
    <div className="dashboard-card">
      <div className="card-header">
        <div>
          <span className="header-label">
            FACTOR RANKING
          </span>

          <h3>Process Pressure Ranking</h3>
        </div>

        <TrendingUp size={22} />
      </div>

      <div
        style={{
          display: "grid",
          gap: "12px",
        }}
      >
        {factors.map((factor, index) => {
          const score = Number(
            factor.score ?? 0
          );

          return (
            <div
              key={factor.station || index}
              style={{
                padding: "14px",
                borderRadius: "10px",
                background: "#0b1118",
                border: "1px solid #263442",
              }}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  gap: "12px",
                }}
              >
                <div>
                  <span className="header-label">
                    RANK {index + 1}
                  </span>

                  <strong
                    style={{
                      display: "block",
                      marginTop: "4px",
                    }}
                  >
                    {factor.station}
                  </strong>
                </div>

                <strong>
                  {formatScore(score)}
                </strong>
              </div>

              <div
                style={{
                  height: "7px",
                  marginTop: "12px",
                  borderRadius: "999px",
                  background: "#18222d",
                  overflow: "hidden",
                }}
              >
                <div
                  style={{
                    width: `${Math.min(
                      score * 100,
                      100
                    )}%`,
                    height: "100%",
                    borderRadius: "999px",
                    background: "#4db3ff",
                  }}
                />
              </div>

              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  marginTop: "9px",
                }}
              >
                <small>
                  Queue pressure:{" "}
                  {formatScore(
                    factor.queue_pressure
                  )}
                </small>

                <small>
                  Utilization pressure:{" "}
                  {formatScore(
                    factor.utilization_pressure
                  )}
                </small>
              </div>
            </div>
          );
        })}
      </div>

      <small className="causality-note">
        Ranking represents process pressure signals
        for investigation. It does not prove that a
        station caused the observed defect.
      </small>
    </div>
  );
}

export default FactorRanking;