import { useApi } from "../hooks/useApi";

function Economics() {
  const { data, loading, error, refresh } = useApi();

  const impact = data?.economics || data?.production_impact || {};
  const production = data?.production || {};

  const formatNumber = (value) =>
    Number(value ?? 0).toLocaleString("en-IN", {
      maximumFractionDigits: 2,
    });

  const formatCurrency = (value) =>
    `₹${Number(value ?? 0).toLocaleString("en-IN", {
      maximumFractionDigits: 0,
    })}`;

  if (loading) {
    return (
      <main className="page-container">
        <section className="page-header">
          <div>
            <span className="header-label">
              PRODUCTION ECONOMICS
            </span>
            <h1>Loading economic model...</h1>
            <p>
              Calculating scrap, rework, and downtime exposure from the
              production data.
            </p>
          </div>
        </section>
      </main>
    );
  }

  if (error) {
    return (
      <main className="page-container">
        <section className="page-header">
          <div>
            <span className="header-label">
              PRODUCTION ECONOMICS
            </span>
            <h1>Economic model unavailable</h1>
            <p>{error}</p>
            <button className="primary-button" onClick={refresh}>
              Retry
            </button>
          </div>
        </section>
      </main>
    );
  }

  return (
    <main className="page-container">
      <section className="page-header">
        <div>
          <span className="header-label">PRODUCTION ECONOMICS</span>

          <h1>Economic Impact</h1>

          <p>
            Quantifying the estimated production impact of defects, scrap,
            rework, and operational downtime from the current dataset and
            assumptions.
          </p>
        </div>
      </section>

      <section className="dashboard-grid">
        <div className="dashboard-card">
          <span>Total Production</span>
          <strong>{formatNumber(production.total_parts)}</strong>
          <small>Total parts in the production dataset</small>
        </div>

        <div className="dashboard-card">
          <span>Estimated Defects</span>
          <strong>{formatNumber(impact.estimated_defective_parts)}</strong>
          <small>Based on the configured defect rate of {Number(impact.assumed_defect_rate ?? 0) * 100}%</small>
        </div>

        <div className="dashboard-card">
          <span>Scrap + Rework</span>
          <strong>{formatCurrency((Number(impact.scrap_cost ?? 0) + Number(impact.rework_cost ?? 0)))}</strong>
          <small>Estimated from defect volume and unit costs</small>
        </div>

        <div className="dashboard-card">
          <span>Total Estimated Impact</span>
          <strong>{formatCurrency(impact.total_estimated_impact)}</strong>
          <small>Including downtime cost for the constrained station</small>
        </div>
      </section>

      <section className="dashboard-card">
        <div className="card-header">
          <div>
            <span className="header-label">ASSUMPTIONS</span>
            <h3>Economic Model Inputs</h3>
          </div>
        </div>

        <div className="impact-list">
          <div>
            <span>Defect rate assumption</span>
            <strong>{Number(impact.assumed_defect_rate ?? 0) * 100}%</strong>
          </div>
          <div>
            <span>Scrap cost per part</span>
            <strong>{formatCurrency(250)}</strong>
          </div>
          <div>
            <span>Rework cost per part</span>
            <strong>{formatCurrency(100)}</strong>
          </div>
          <div>
            <span>Downtime cost per hour</span>
            <strong>{formatCurrency(1500)}</strong>
          </div>
        </div>

        <small className="causality-note">
          {impact.note || "These values are configurable assumptions for the demonstration model and should not be treated as actual proven financial results."}
        </small>
      </section>
    </main>
  );
}

export default Economics;