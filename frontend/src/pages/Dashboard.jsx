import {
  Activity,
  AlertTriangle,
  Factory,
  IndianRupee,
  TrendingUp,
  ShieldCheck,
  ArrowRight,
} from "lucide-react";

import StatCard from "../components/dashboard/StatCard";
import { useApi } from "../hooks/useApi";

function Dashboard() {
  const { data, loading, error, refresh } = useApi();

  if (loading) {
    return (
      <main className="page-container">
        <section className="page-header">
          <span className="header-label">SYSTEM ANALYSIS</span>
          <h1>Loading industrial analysis...</h1>
          <p>
            Connecting to the AI decision-support backend.
          </p>
        </section>
      </main>
    );
  }

  if (error) {
    return (
      <main className="page-container">
        <section className="page-header">
          <span className="header-label">SYSTEM ERROR</span>
          <h1>Unable to load analysis</h1>
          <p>{error}</p>

          <button
            className="primary-button"
            onClick={refresh}
          >
            <Activity size={17} />
            Retry Analysis
          </button>
        </section>
      </main>
    );
  }

  const processData = Array.isArray(data?.process?.analysis)
    ? data.process.analysis
    : Array.isArray(data?.process?.process_analysis)
      ? data.process.process_analysis
      : Array.isArray(data?.process_analysis)
        ? data.process_analysis
        : [];

  const topProcess =
    data?.process?.top_process_candidate ||
    data?.top_process_candidate ||
    processData[0] ||
    null;

  const rootCause = data?.root_cause || {};
  const impact =
    data?.economics ||
    data?.production_impact ||
    {};

  const productionVolume =
    impact?.total_parts ?? 0;

  const averageThroughput =
    impact?.average_parts_per_hour ?? 0;

  const totalImpact =
    impact?.total_estimated_impact ?? 0;

  const estimatedDefects =
    impact?.estimated_defective_parts ?? 0;

  const formatNumber = (value) =>
    Number(value || 0).toLocaleString("en-IN", {
      maximumFractionDigits: 0,
    });

  const formatDecimal = (value) =>
    Number(value || 0).toLocaleString("en-IN", {
      maximumFractionDigits: 2,
    });

  const formatCurrency = (value) =>
    `₹${Number(value || 0).toLocaleString("en-IN", {
      maximumFractionDigits: 0,
    })}`;

  return (
    <main className="page-container">

      {/* =====================================================
          DASHBOARD HEADER
          ===================================================== */}

      <section className="page-header">
        <div>
          <span className="header-label">
            INDUSTRIAL OPERATIONS
          </span>

          <h1>Production Intelligence Dashboard</h1>

          <p>
            Unified decision support across production flow,
            visual inspection, process pressure, root-cause
            evidence, and estimated economic impact.
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


      {/* =====================================================
          KPI SUMMARY
          ===================================================== */}

      <section className="dashboard-grid">

        <StatCard
          label="Production Volume"
          value={formatNumber(productionVolume)}
          description="Total parts analyzed"
          icon={<Factory size={18} />}
        />

        <StatCard
          label="Average Throughput"
          value={`${formatDecimal(
            averageThroughput
          )} / hr`}
          description="Average production rate"
          icon={<TrendingUp size={18} />}
        />

        <StatCard
          label="Top Process Candidate"
          value={topProcess?.station || "N/A"}
          description={`Pressure score: ${formatDecimal(
            topProcess?.score
          )}`}
          icon={<AlertTriangle size={18} />}
        />

        <StatCard
          label="Estimated Impact"
          value={formatCurrency(totalImpact)}
          description={`${formatNumber(
            estimatedDefects
          )} estimated defective parts`}
          icon={<IndianRupee size={18} />}
        />

      </section>


      {/* =====================================================
          PRODUCTION FLOW
          ===================================================== */}

      <section className="dashboard-card system-overview">

        <div className="card-header">

          <div>
            <span className="header-label">
              PROCESS ANALYSIS
            </span>

            <h3>
              Production Flow Pressure
            </h3>

            <p>
              Current process utilization and queue
              conditions across manufacturing stations.
            </p>
          </div>

          <div className="system-status">
            <span className="status-dot online" />
            Analysis Ready
          </div>

        </div>

        {processData.length > 0 ? (
          <div className="production-flow">

            {processData.map((station, index) => {

              const utilization =
                Number(station.utilization || 0) * 100;

              const score =
                Number(station.score || 0);

              const isTop =
                station.station ===
                topProcess?.station;

              return (
                <div
                  className={`flow-station ${
                    isTop
                      ? "flow-station-highlight"
                      : ""
                  }`}
                  key={station.station}
                >

                  <div className="flow-station-header">

                    <strong>
                      {station.station}
                    </strong>

                    {isTop && (
                      <span className="flow-candidate">
                        Top Candidate
                      </span>
                    )}

                    <span>
                      {formatDecimal(
                        utilization
                      )}%
                    </span>

                  </div>

                  <div className="flow-progress">

                    <div
                      className="flow-progress-bar"
                      style={{
                        width: `${Math.min(
                          utilization,
                          100
                        )}%`,
                      }}
                    />

                  </div>

                  <div className="flow-station-meta">

                    <small>
                      Queue:{" "}
                      {formatDecimal(
                        station.avg_queue
                      )}
                    </small>

                    <small>
                      Pressure:{" "}
                      {formatDecimal(score)}
                    </small>

                  </div>

                  {index <
                    processData.length - 1 && (
                    <div className="flow-arrow">
                      <ArrowRight size={18} />
                    </div>
                  )}

                </div>
              );
            })}

          </div>
        ) : (
          <div className = " empty-state ">
            <Factory size={28} />
            <h3>No process data available</h3>
            <p>
              Manufacturing process analysis is
              currently unavailable.
            </p>
          </div>
        )}

      </section>


      {/* =====================================================
          AI INVESTIGATION + ECONOMICS
          ===================================================== */}

      <section className="dashboard-grid dashboard-grid-two">

        {/* ROOT CAUSE */}

        <div className="dashboard-card">

          <div className="card-header">

            <div>
              <span className="header-label">
                AI INVESTIGATION
              </span>

              <h3>
                Root-Cause Evidence
              </h3>
            </div>

            <ShieldCheck
              size={20}
            />

          </div>

          <div className="analysis-highlight">

            <span>
              Detected defect
            </span>

            <strong>
              {rootCause?.defect || "N/A"}
            </strong>

          </div>

          <div className="analysis-highlight">

            <span>
              Likely contributing factor
            </span>

            <strong>
              {rootCause?.likely_contributing_factor ||
                "N/A"}
            </strong>

          </div>

          <p className="analysis-text">
            {rootCause?.recommendation ||
              "No recommendation available."}
          </p>

          <small className="causality-note">
            {rootCause?.causality_note ||
              "Process evidence is an investigation hypothesis, not proof of causality."}
          </small>

        </div>


        {/* ECONOMICS */}

        <div className="dashboard-card">

          <div className="card-header">

            <div>
              <span className="header-label">
                ECONOMIC IMPACT
              </span>

              <h3>
                Production Cost Exposure
              </h3>
            </div>

            <IndianRupee
              size={20}
            />

          </div>

          <div className="impact-list">

            <div>
              <span>
                Estimated defective parts
              </span>

              <strong>
                {formatNumber(
                  estimatedDefects
                )}
              </strong>
            </div>

            <div>
              <span>
                Scrap cost
              </span>

              <strong>
                {formatCurrency(
                  impact?.scrap_cost
                )}
              </strong>
            </div>

            <div>
              <span>
                Rework cost
              </span>

              <strong>
                {formatCurrency(
                  impact?.rework_cost
                )}
              </strong>
            </div>

            <div className="impact-total">

              <span>
                Total estimated impact
              </span>

              <strong>
                {formatCurrency(
                  totalImpact
                )}
              </strong>

            </div>

          </div>

          <small className="causality-note">
            Economic values are configurable
            assumptions for the demonstration.
          </small>

        </div>

      </section>


      {/* =====================================================
          PROCESS PRESSURE TABLE
          ===================================================== */}

      <section className="dashboard-card">

        <div className="card-header">

          <div>
            <span className="header-label">
              PROCESS PRESSURE
            </span>

            <h3>
              Station Analysis
            </h3>

            <p>
              Combined queue and utilization pressure
              used to identify investigation candidates.
            </p>
          </div>

        </div>

        {processData.length > 0 ? (
          <div className="table-wrapper">

            <table className="analysis-table">

              <thead>
                <tr>
                  <th>Station</th>
                  <th>Average Queue</th>
                  <th>Utilization</th>
                  <th>Pressure Score</th>
                </tr>
              </thead>

              <tbody>                                      
                {processData.map(
                  (station) => {

                    const isTop =
                      station.station ===
                      topProcess?.station;

                    return (
                      <tr
                        key={station.station}
                        className={
                          isTop
                            ? "top-process-row"
                            : ""
                        }
                      >

                        <td>
                          <strong>
                            {station.station}
                          </strong>

                          {isTop && (
                            <span className="table-candidate">
                              Top candidate
                            </span>
                          )}
                        </td>

                        <td>
                          {formatDecimal(
                            station.avg_queue
                          )}
                        </td>

                        <td>
                          {formatDecimal(
                            station.utilization *
                              100
                          )}%
                        </td>

                        <td>
                          <span className="score-badge">
                            {formatDecimal(
                              station.score
                            )}
                          </span>
                        </td>

                      </tr>
                    );
                  }
                )}

              </tbody>

            </table>

          </div>
        ) : (
          <div className="empty-state">
            <AlertTriangle size={28} />
            <h3>No station analysis</h3>
            <p>
              Process pressure data could not be loaded.
            </p>
          </div>
        )}

      </section>

    </main>
  );
}

export default Dashboard;