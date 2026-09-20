import { useApi } from "../hooks/useApi";
import { Factory, Activity, Clock } from "lucide-react";

function Production() {
  const { data, loading, error, refresh } = useApi();

  if (loading) {
    return (
      <main className="page-container">
        <section className="page-header">
          <span className="header-label">
            PRODUCTION ANALYTICS
          </span>
          <h1>Loading production data...</h1>
          <p>Analyzing manufacturing process data.</p>
        </section>
      </main>
    );
  }

  if (error) {
    return (
      <main className="page-container">
        <section className="page-header">
          <span className="header-label">
            SYSTEM ERROR
          </span>
          <h1>Unable to load production data</h1>
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

  const stations = Array.isArray(data?.process?.analysis)
    ? data.process.analysis
    : Array.isArray(data?.process?.process_analysis)
      ? data.process.process_analysis
      : Array.isArray(data?.process_analysis)
        ? data.process_analysis
        : [];

  const production = data?.production || {};

  const formatNumber = (value) =>
    Number(value ?? 0).toLocaleString("en-IN", {
      maximumFractionDigits: 2,
    });

  const formatPercent = (value) =>
    `${(Number(value ?? 0) * 100).toFixed(1)}%`;

  return (
    <main className="page-container">
      <section className="page-header">
        <div>
          <span className="header-label">
            PRODUCTION ANALYTICS
          </span>

          <h1>Manufacturing Process</h1>

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
        <div className="dashboard-card">
          <div className="card-header">
            <div>
              <span className="header-label">MODEL 1</span>
              <h3>Production Summary</h3>
            </div>
            <Factory size={22} />
          </div>
          <div className="analysis-highlight">
            <span>Total Parts</span>
            <strong>{formatNumber(production.total_parts)}</strong>
          </div>
          <div className="analysis-highlight">
            <span>Average Throughput</span>
            <strong>{formatNumber(production.average_parts_per_hour)}/hr</strong>
          </div>
          <div className="analysis-highlight">
            <span>Average Demand</span>
            <strong>{formatNumber(production.average_demand)}</strong>
          </div>
        </div>

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