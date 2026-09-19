import { useApi } from "../hooks/useApi";
import { Factory, Activity, Clock } from "lucide-react";

function Production() {
  const { data, loading, error, refresh } = useApi();

  if (loading) {
    return (
      <main className="page-content">
        <section className="welcome-section">
          <span className="header-label">
            PRODUCTION ANALYTICS
          </span>
          <h2>Loading production data...</h2>
          <p>Analyzing manufacturing process data.</p>
        </section>
      </main>
    );
  }

  if (error) {
    return (
      <main className="page-content">
        <section className="welcome-section">
          <span className="header-label">
            SYSTEM ERROR
          </span>
          <h2>Unable to load production data</h2>
          <p>{error}</p>

          <button
            className="primary-button"
            onClick={refresh}
          >
            Retry Analysis
          </button>
        </section>
      </main>
    );
  }

  const stations =
    data?.process?.process_analysis || [];

  const formatNumber = (value) =>
    Number(value ?? 0).toLocaleString("en-IN", {
      maximumFractionDigits: 2,
    });

  const formatPercent = (value) =>
    `${(Number(value ?? 0) * 100).toFixed(1)}%`;

  return (
    <main className="page-content">
      <section className="welcome-section">
        <div>
          <span className="header-label">
            PRODUCTION ANALYTICS
          </span>

          <h2>Manufacturing Process</h2>

          <p>
            Monitor queue pressure, utilization,
            and process performance across
            production stations.
          </p>
        </div>

        <button
          className="primary-button"
          onClick={refresh}
        >
          <Activity size={17} />
          Refresh Analysis
        </button>
      </section>

      <section className="dashboard-grid">
        {stations.map((station) => (
          <div
            className="dashboard-card"
            key={station.station}
          >
            <div className="card-header">
              <div>
                <span className="header-label">
                  STATION
                </span>

                <h3>{station.station}</h3>
              </div>

              <Factory size={22} />
            </div>

            <div className="analysis-highlight">
              <span>Utilization</span>

              <strong>
                {formatPercent(
                  station.utilization
                )}
              </strong>
            </div>

            <div className="analysis-highlight">
              <span>Average Queue</span>

              <strong>
                {formatNumber(
                  station.avg_queue
                )}
              </strong>
            </div>

            <div className="analysis-highlight">
              <span>Pressure Score</span>

              <strong>
                {formatNumber(
                  station.score
                )}
              </strong>
            </div>
          </div>
        ))}
      </section>

      <section className="dashboard-card">
        <div className="card-header">
          <div>
            <span className="header-label">
              PROCESS PERFORMANCE
            </span>

            <h3>Station Performance</h3>
          </div>

          <Clock size={21} />
        </div>

        <div className="table-wrapper">
          <table className="analysis-table">
            <thead>
              <tr>
                <th>Station</th>
                <th>Average Queue</th>
                <th>Utilization</th>
                <th>Queue Pressure</th>
                <th>Utilization Pressure</th>
                <th>Pressure Score</th>
              </tr>
            </thead>

            <tbody>
              {stations.map((station) => (
                <tr key={station.station}>
                  <td>
                    <strong>
                      {station.station}
                    </strong>
                  </td>

                  <td>
                    {formatNumber(
                      station.avg_queue
                    )}
                  </td>

                  <td>
                    {formatPercent(
                      station.utilization
                    )}
                  </td>

                  <td>
                    {formatNumber(
                      station.queue_pressure
                    )}
                  </td>

                  <td>
                    {formatNumber(
                      station.utilization_pressure
                    )}
                  </td>

                  <td>
                    <span className="score-badge">
                      {formatNumber(
                        station.score
                      )}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </main>
  );
}

export default Production;