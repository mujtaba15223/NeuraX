import { useEffect, useState } from "react";
import {
  RefreshCw,
  Factory,
  AlertTriangle,
  BarChart3,
} from "lucide-react";

import { getBottleneck } from "../services/api";

function Bottleneck() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchAnalysis = async () => {
    try {
      setLoading(true);
      setError("");

      const result = await getBottleneck();

      setData(result);
    } catch (err) {
      setError(
        err.message ||
          "Unable to connect to bottleneck analysis."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalysis();
  }, []);

  if (loading) {
    return (
      <div className="page-container">
        <div className="page-header">
          <div>
            <span className="header-label">
              BOTTLENECK ANALYTICS
            </span>

            <h1>Production Bottlenecks</h1>

            <p>
              Analyze queue pressure, utilization,
              and production flow constraints.
            </p>
          </div>
        </div>

        <div className="dashboard-card">
          <div className="empty-state">
            <RefreshCw
              size={28}
              className="spin"
            />

            <p>
              Analyzing production stations...
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page-container">
        <div className="page-header">
          <div>
            <span className="header-label">
              BOTTLENECK ANALYTICS
            </span>

            <h1>Production Bottlenecks</h1>

            <p>
              Analyze queue pressure, utilization,
              and production flow constraints.
            </p>
          </div>
        </div>

        <div className="dashboard-card">
          <div className="empty-state">
            <AlertTriangle size={30} />

            <h3>
              Analysis Unavailable
            </h3>

            <p>{error}</p>

            <button
              className="action-button"
              onClick={fetchAnalysis}
            >
              <RefreshCw size={16} />
              Retry Analysis
            </button>
          </div>
        </div>
      </div>
    );
  }

  const processAnalysis = Array.isArray(
    data?.stations
  )
    ? data.stations
    : [];

  const stations = processAnalysis
    .map((values, index) => ({
      station:
        values?.station ||
        `Station ${index + 1}`,

      queue: Number(
        values?.avg_queue ?? values?.queue_time ?? 0
      ),

      utilization: Number(
        values?.utilization ?? 0
      ),

      queuePressure: Number(
        values?.queue_pressure ?? 0
      ),

      utilizationPressure: Number(
        values?.utilization_pressure ?? 0
      ),

      score: Number(
        values?.score ?? values?.pressure_score ?? 0
      ),

      rank:
        Number(values?.rank) ||
        index + 1,
    }))
    .sort(
      (a, b) => b.score - a.score
    )
    .map((station, index) => ({
      ...station,
      rank: index + 1,
    }));

  const topStation =
    stations[0] || null;

  const defectAwareStations = Array.isArray(
    data?.defect_aware_stations
  )
    ? data.defect_aware_stations
        .map((values, index) => ({
          station: values?.station || `Station ${index + 1}`,
          score: Number(values?.defect_aware_score ?? 0),
          adjustment: Number(values?.defect_adjustment ?? 1),
        }))
        .sort((a, b) => b.score - a.score)
    : [];

  const defectAwareTop = defectAwareStations[0] || null;

  const activeTopStation =
    defectAwareTop || topStation;

  const isDefectAware = Boolean(
    defectAwareTop
  );

  return (
    <div className="page-container">

      {/* HEADER */}
      <div className="page-header">
        <div>
          <span className="header-label">
            BOTTLENECK ANALYTICS
          </span>

          <h1>Production Bottlenecks</h1>

          <p>
            Identify process stations with the
            strongest combined queue and
            utilization pressure.
          </p>
        </div>

        <button
          className="action-button"
          onClick={fetchAnalysis}
        >
          <RefreshCw size={16} />
          Refresh Analysis
        </button>
      </div>


      {/* TOP PROCESS CANDIDATE */}
      {activeTopStation && (
        <div className="dashboard-card bottleneck-highlight">

          <div className="highlight-icon">
            <AlertTriangle size={28} />
          </div>

          <div>
            <span className="header-label">
              {isDefectAware
                ? "DEFECT-AWARE PROCESS CANDIDATE"
                : "BASE PROCESS CANDIDATE"}
            </span>

            <h2>
              {topStation.station}
            </h2>

            <p>
              {isDefectAware
                ? `For the detected ${data.defect_type} anomaly, this station has the strongest defect-aware relevance based on measured process pressure and engineering priors.`
                : "This station currently has the highest measured combined process-pressure score in the production flow."}
            </p>
          </div>

          <div className="highlight-score">
            <span>
              Pressure Score
            </span>

            <strong>
              {activeTopStation.score.toFixed(3)}
            </strong>

            <small>
              {isDefectAware
                ? "Investigation signal"
                : `Rank #${activeTopStation.rank}`}
            </small>
          </div>

        </div>
      )}


      {/* NO DATA */}
      {!activeTopStation && (
        <div className="dashboard-card">
          <div className="empty-state">
            <BarChart3 size={30} />

            <h3>
              No Process Data
            </h3>

            <p>
              The backend returned no station-level
              bottleneck analysis.
            </p>
          </div>
        </div>
      )}

      {defectAwareStations.length > 0 && (
        <div className="dashboard-card">
          <div className="card-header">
            <div>
              <span className="header-label">
                DEFECT-AWARE PROCESS RELEVANCE
              </span>
              <h3>
                {data.defect_type || "Detected anomaly"} investigation signal
              </h3>
            </div>
            <AlertTriangle size={22} />
          </div>

          <p>
            This layer applies engineering priors to the measured process
            pressure. It is an investigation hypothesis, not proof of cause.
          </p>

          <div className="impact-list">
            {defectAwareStations.map((station) => (
              <div key={station.station}>
                <span>{station.station}</span>
                <strong>{station.score.toFixed(3)}</strong>
              </div>
            ))}
          </div>

          {defectAwareTop && (
            <small className="causality-note">
              Strongest defect-aware process candidate: {defectAwareTop.station}.
            </small>
          )}
        </div>
      )}


      {/* STATION CARDS */}
      <div className="dashboard-grid">

        {stations.map((station) => (

          <div
            className="dashboard-card station-card"
            key={station.station}
          >

            <div className="card-header">

              <div>
                <span className="header-label">
                  STATION #{station.rank}
                </span>

                <h3>
                  {station.station}
                </h3>
              </div>

              <Factory size={22} />

            </div>


            <div className="station-score">

              <span>
                Pressure Score
              </span>

              <strong>
                {station.score.toFixed(3)}
              </strong>

            </div>


            <div className="metric-row">

              <span>
                Average Queue
              </span>

              <strong>
                {station.queue.toFixed(3)}
              </strong>

            </div>


            <div className="metric-row">

              <span>
                Utilization
              </span>

              <strong>
                {(station.utilization * 100).toFixed(1)}
                %
              </strong>

            </div>


            <div className="metric-row">

              <span>
                Queue Pressure
              </span>

              <strong>
                {(station.queuePressure * 100).toFixed(1)}
                %
              </strong>

            </div>


            <div className="metric-row">

              <span>
                Utilization Pressure
              </span>

              <strong>
                {(
                  station.utilizationPressure * 100
                ).toFixed(1)}
                %
              </strong>

            </div>

          </div>

        ))}

      </div>


      {/* COMPARISON TABLE */}
      {stations.length > 0 && (

        <div className="dashboard-card">

          <div className="card-header">

            <div>
              <span className="header-label">
                PROCESS PRESSURE
              </span>

              <h3>
                Station Comparison
              </h3>
            </div>

            <BarChart3 size={22} />

          </div>


          <div className="table-wrapper">

            <table className="data-table">

              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Station</th>
                  <th>Avg Queue</th>
                  <th>Utilization</th>
                  <th>Queue Pressure</th>
                  <th>Util. Pressure</th>
                  <th>Score</th>
                </tr>
              </thead>


              <tbody>

                {stations.map((station) => (

                  <tr
                    key={station.station}
                  >

                    <td>
                      #{station.rank}
                    </td>

                    <td>
                      <strong>
                        {station.station}
                      </strong>
                    </td>

                    <td>
                      {station.queue.toFixed(3)}
                    </td>

                    <td>
                      {(station.utilization * 100).toFixed(1)}
                      %
                    </td>

                    <td>
                      {(station.queuePressure * 100).toFixed(1)}
                      %
                    </td>

                    <td>
                      {(
                        station.utilizationPressure * 100
                      ).toFixed(1)}
                      %
                    </td>

                    <td>
                      <strong>
                        {station.score.toFixed(3)}
                      </strong>
                    </td>

                  </tr>

                ))}

              </tbody>

            </table>

          </div>

        </div>

      )}


      {/* CAUSALITY WARNING */}
      <div className="dashboard-card causality-warning">

        <div className="warning-icon">
          <AlertTriangle size={20} />
        </div>

        <div>

          <strong>
            Bottleneck Interpretation
          </strong>

          <p>
            A high pressure score identifies a
            process constraint candidate based on
            queue and utilization evidence. It does
            not by itself prove that the station is
            the cause of a product defect.
          </p>

        </div>

      </div>

    </div>
  );
}

export default Bottleneck;