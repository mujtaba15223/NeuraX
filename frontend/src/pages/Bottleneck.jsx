import { useEffect, useState } from "react";
import {
  RefreshCw,
  Factory,
  AlertTriangle,
  BarChart3,
  Gauge,
  Clock3,
  Target,
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

  const processAnalysis =
    Array.isArray(data?.stations)
      ? data.stations
      : [];

  const stations = processAnalysis
    .map((values, index) => ({
      station:
        values?.station ||
        `Station ${index + 1}`,

      queue: Number(
        values?.avg_queue ??
          values?.queue_time ??
          0
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
        values?.score ??
          values?.pressure_score ??
          0
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

  const defectAwareStations =
    Array.isArray(
      data?.defect_aware_stations
    )
      ? data.defect_aware_stations
          .map((values, index) => ({
            station:
              values?.station ||
              `Station ${index + 1}`,

            score: Number(
              values?.defect_aware_score ??
                0
            ),

            adjustment: Number(
              values?.defect_adjustment ??
                1
            ),
          }))
          .sort(
            (a, b) =>
              b.score - a.score
          )
      : [];

  const defectAwareTop =
    defectAwareStations[0] || null;

  const activeTopStation =
    defectAwareTop || topStation;

  const isDefectAware =
    Boolean(defectAwareTop);

  const maxScore =
    stations.length > 0
      ? Math.max(
          ...stations.map(
            (station) => station.score
          )
        )
      : 1;

  return (
    <div className="page-container">

      {/* HEADER */}
      <div className="page-header">
        <div>
          <span className="header-label">
            BOTTLENECK ANALYTICS
          </span>

          <h1>
            Production Bottlenecks
          </h1>

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

      {/* INVESTIGATION SUMMARY */}
      {activeTopStation && (
        <div className="dashboard-card bottleneck-highlight">
          <div className="highlight-icon">
            <AlertTriangle size={28} />
          </div>

          <div>
            <span className="header-label">
              {isDefectAware
                ? "DEFECT-AWARE PROCESS CANDIDATE"
                : "TOP PROCESS PRESSURE CANDIDATE"}
            </span>

            <h2>
              {activeTopStation.station}
            </h2>

            <p>
              {isDefectAware
                ? `For the detected ${
                    data?.defect_type ||
                    "anomaly"
                  }, this station has the strongest defect-aware relevance based on measured process pressure and engineering priors.`
                : "This station currently has the highest measured combined process-pressure score in the production flow."}
            </p>
          </div>

          <div className="highlight-score">
            <span>
              Pressure Score
            </span>

            <strong>
              {activeTopStation.score.toFixed(
                3
              )}
            </strong>

            <small>
              {isDefectAware
                ? "Investigation signal"
                : "Highest process score"}
            </small>
          </div>
        </div>
      )}

      {/* KEY METRICS */}
      {topStation && (
        <div className="dashboard-grid">

          <div className="dashboard-card">
            <div className="card-header">
              <div>
                <span className="header-label">
                  TOP CONSTRAINT
                </span>

                <h3>
                  {topStation.station}
                </h3>
              </div>

              <Factory size={22} />
            </div>

            <div className="station-score">
              <span>
                Combined Pressure
              </span>

              <strong>
                {topStation.score.toFixed(3)}
              </strong>
            </div>

            <p className="control-description">
              Highest combined queue and
              utilization pressure among the
              analyzed stations.
            </p>
          </div>

          <div className="dashboard-card">
            <div className="card-header">
              <div>
                <span className="header-label">
                  QUEUE SIGNAL
                </span>

                <h3>
                  {topStation.queue.toFixed(3)}
                </h3>
              </div>

              <Clock3 size={22} />
            </div>

            <p className="control-description">
              Average queue measurement for the
              top process-pressure candidate.
            </p>

            <div className="metric-row">
              <span>
                Queue Pressure
              </span>

              <strong>
                {(
                  topStation.queuePressure *
                  100
                ).toFixed(1)}
                %
              </strong>
            </div>
          </div>

          <div className="dashboard-card">
            <div className="card-header">
              <div>
                <span className="header-label">
                  UTILIZATION SIGNAL
                </span>

                <h3>
                  {(
                    topStation.utilization *
                    100
                  ).toFixed(1)}
                  %
                </h3>
              </div>

              <Gauge size={22} />
            </div>

            <p className="control-description">
              Measured station utilization for
              the top process-pressure candidate.
            </p>

            <div className="metric-row">
              <span>
                Utilization Pressure
              </span>

              <strong>
                {(
                  topStation.utilizationPressure *
                  100
                ).toFixed(1)}
                %
              </strong>
            </div>
          </div>
        </div>
      )}

      {/* DEFECT-AWARE ANALYSIS */}
      {defectAwareStations.length > 0 && (
        <div className="dashboard-card">
          <div className="card-header">
            <div>
              <span className="header-label">
                DEFECT-AWARE PROCESS RELEVANCE
              </span>

              <h3>
                {data?.defect_type ||
                  "Detected anomaly"}{" "}
                Investigation Signal
              </h3>
            </div>

            <Target size={22} />
          </div>

          <p>
            This layer combines measured process
            pressure with engineering priors for
            the detected defect. It is an
            investigation hypothesis, not proof
            of causality.
          </p>

          <div className="impact-list">
            {defectAwareStations.map(
              (station, index) => (
                <div
                  key={station.station}
                >
                  <span>
                    #{index + 1}{" "}
                    {station.station}
                  </span>

                  <strong>
                    {station.score.toFixed(3)}
                  </strong>
                </div>
              )
            )}
          </div>

          {defectAwareTop && (
            <small className="causality-note">
              Strongest defect-aware process
              candidate:{" "}
              <strong>
                {defectAwareTop.station}
              </strong>
              .
            </small>
          )}
        </div>
      )}

      {/* STATION CARDS */}
      <div className="dashboard-grid">
        {stations.map((station) => {
          const scorePercent =
            maxScore > 0
              ? Math.min(
                  100,
                  (station.score /
                    maxScore) *
                    100
                )
              : 0;

          return (
            <div
              className={`dashboard-card station-card ${
                station.rank === 1
                  ? "top-process-row"
                  : ""
              }`}
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

              <div className="flow-progress">
                <div
                  className="flow-progress-bar"
                  style={{
                    width: `${scorePercent}%`,
                  }}
                />
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
                  {(
                    station.utilization *
                    100
                  ).toFixed(1)}
                  %
                </strong>
              </div>

              <div className="metric-row">
                <span>
                  Queue Pressure
                </span>

                <strong>
                  {(
                    station.queuePressure *
                    100
                  ).toFixed(1)}
                  %
                </strong>
              </div>

              <div className="metric-row">
                <span>
                  Utilization Pressure
                </span>

                <strong>
                  {(
                    station.utilizationPressure *
                    100
                  ).toFixed(1)}
                  %
                </strong>
              </div>
            </div>
          );
        })}
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
                {stations.map(
                  (station) => (
                    <tr
                      key={
                        station.station
                      }
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
                        {station.queue.toFixed(
                          3
                        )}
                      </td>

                      <td>
                        {(
                          station.utilization *
                          100
                        ).toFixed(1)}
                        %
                      </td>

                      <td>
                        {(
                          station.queuePressure *
                          100
                        ).toFixed(1)}
                        %
                      </td>

                      <td>
                        {(
                          station.utilizationPressure *
                          100
                        ).toFixed(1)}
                        %
                      </td>

                      <td>
                        <strong>
                          {station.score.toFixed(
                            3
                          )}
                        </strong>
                      </td>
                    </tr>
                  )
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* METHODOLOGY */}
      <div className="dashboard-card">
        <div className="card-header">
          <div>
            <span className="header-label">
              DECISION LOGIC
            </span>

            <h3>
              How Bottleneck Pressure Is Evaluated
            </h3>
          </div>

          <BarChart3 size={22} />
        </div>

        <div className="analysis-flow">
          <div className="flow-step">
            <span className="flow-number">
              01
            </span>

            <div>
              <strong>
                Queue Evidence
              </strong>

              <p>
                Measure the relative queue
                pressure at each production
                station.
              </p>
            </div>
          </div>

          <div className="flow-arrow">
            →
          </div>

          <div className="flow-step">
            <span className="flow-number">
              02
            </span>

            <div>
              <strong>
                Utilization Evidence
              </strong>

              <p>
                Measure relative station
                utilization to identify capacity
                pressure.
              </p>
            </div>
          </div>

          <div className="flow-arrow">
            →
          </div>

          <div className="flow-step">
            <span className="flow-number">
              03
            </span>

            <div>
              <strong>
                Combined Pressure
              </strong>

              <p>
                Combine queue and utilization
                signals into a comparable station
                pressure score.
              </p>
            </div>
          </div>

          <div className="flow-arrow">
            →
          </div>

          <div className="flow-step">
            <span className="flow-number">
              04
            </span>

            <div>
              <strong>
                Constraint Candidate
              </strong>

              <p>
                Rank stations to identify where
                engineering investigation may
                provide the most value.
              </p>
            </div>
          </div>
        </div>
      </div>

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
            queue and utilization evidence. It
            does not by itself prove that the
            station caused a product defect.
            Bottleneck analysis should be combined
            with visual and process evidence before
            taking corrective action.
          </p>
        </div>
      </div>
    </div>
  );
}

export default Bottleneck;