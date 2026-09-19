import {
  Activity,
  AlertTriangle,
  Factory,
  IndianRupee,
  TrendingUp,
} from "lucide-react";

import StatCard from "../components/dashboard/StatCard";
import { useApi } from "../hooks/useApi";

function Dashboard() {
  const { data, loading, error, refresh } = useApi();

  if (loading) {
    return (
      <main className="page-content">
        <section className="welcome-section">
          <span className="header-label">SYSTEM ANALYSIS</span>
          <h2>Loading industrial analysis...</h2>
          <p>Connecting to the AI decision-support backend.</p>
        </section>
      </main>
    );
  }

  if (error) {
    return (
      <main className="page-content">
        <section className="welcome-section">
          <span className="header-label">SYSTEM ERROR</span>
          <h2>Unable to load analysis</h2>
          <p>{error}</p>

          <button className="primary-button" onClick={refresh}>
            Retry Analysis
          </button>
        </section>
      </main>
    );
  }

  const processData = data?.process?.process_analysis || [];
  const topProcess = data?.process?.top_process_candidate;
  const rootCause = data?.root_cause;
  const impact = data?.production_impact;

  const productionVolume = impact?.total_parts ?? 0;
  const averageThroughput = impact?.average_parts_per_hour ?? 0;
  const totalImpact = impact?.total_estimated_impact ?? 0;
  const estimatedDefects = impact?.estimated_defective_parts ?? 0;

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
    <main className="page-content">
      <section className="welcome-section">
        <div>
          <span className="header-label">INDUSTRIAL OPERATIONS</span>
          <h2>Production Intelligence Dashboard</h2>
          <p>
            Unified view of production flow, process pressure, root-cause
            evidence, and estimated economic impact.
          </p>
        </div>

        <button className="primary-button" onClick={refresh}>
          <Activity size={17} />
          Refresh Analysis
        </button>
      </section>

      <section className="dashboard-grid">
        <StatCard
          label="Production Volume"
          value={formatNumber(productionVolume)}
          description="Total parts analyzed"
          icon={<Factory size={18} />}
        />

        <StatCard
          label="Average Throughput"
          value={`${formatDecimal(averageThroughput)} / hr`}
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

      <section className="dashboard-card system-overview">
        <div className="card-header">
          <div>
            <span className="header-label">PROCESS ANALYSIS</span>
            <h3>Station Pressure Overview</h3>
          </div>

          <div className="system-status">
            <span className="status-dot" />
            Analysis Ready
          </div>
        </div>

        <div className="production-flow">
          {processData.map((station, index) => (
            <div className="flow-station" key={station.station}>
              <div className="flow-station-header">
                <strong>{station.station}</strong>
                <span>
                  {formatDecimal(station.utilization * 100)}%
                </span>
              </div>

              <div className="flow-progress">
                <div
                  className="flow-progress-bar"
                  style={{
                    width: `${Math.min(
                      Number(station.utilization || 0) * 100,
                      100
                    )}%`,
                  }}
                />
              </div>

              <small>
                Queue: {formatDecimal(station.avg_queue)}
              </small>

              {index < processData.length - 1 && (
                <div className="flow-arrow">→</div>
              )}
            </div>
          ))}
        </div>
      </section>

      <section className="dashboard-grid dashboard-grid-two">
        <div className="dashboard-card">
          <div className="card-header">
            <div>
              <span className="header-label">ROOT CAUSE</span>
              <h3>Investigation Signal</h3>
            </div>
          </div>

          <div className="analysis-highlight">
            <span>Detected defect</span>
            <strong>{rootCause?.defect || "N/A"}</strong>
          </div>

          <div className="analysis-highlight">
            <span>Likely contributing factor</span>
            <strong>
              {rootCause?.likely_contributing_factor || "N/A"}
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

        <div className="dashboard-card">
          <div className="card-header">
            <div>
              <span className="header-label">ECONOMIC IMPACT</span>
              <h3>Production Cost Exposure</h3>
            </div>
          </div>

          <div className="impact-list">
            <div>
              <span>Estimated defective parts</span>
              <strong>{formatNumber(estimatedDefects)}</strong>
            </div>

            <div>
              <span>Scrap cost</span>
              <strong>
                {formatCurrency(impact?.scrap_cost)}
              </strong>
            </div>

            <div>
              <span>Rework cost</span>
              <strong>
                {formatCurrency(impact?.rework_cost)}
              </strong>
            </div>

            <div>
              <span>Total estimated impact</span>
              <strong>
                {formatCurrency(totalImpact)}
              </strong>
            </div>
          </div>

          <small className="causality-note">
            Economic values are configurable assumptions for the
            demonstration.
          </small>
        </div>
      </section>

      <section className="dashboard-card">
        <div className="card-header">
          <div>
            <span className="header-label">PROCESS PRESSURE</span>
            <h3>Station Analysis</h3>
          </div>
        </div>

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
              {processData.map((station) => (
                <tr key={station.station}>
                  <td>
                    <strong>{station.station}</strong>
                  </td>
                  <td>{formatDecimal(station.avg_queue)}</td>
                  <td>
                    {formatDecimal(station.utilization * 100)}%
                  </td>
                  <td>
                    <span className="score-badge">
                      {formatDecimal(station.score)}
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

export default Dashboard;