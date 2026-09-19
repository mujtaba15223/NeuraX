function Economics() {
  return (
    <main className="page-content">
      <section className="welcome-section">
        <span className="section-label">PRODUCTION ECONOMICS</span>

        <h1>Economic Impact</h1>

        <p>
          Quantify the estimated production impact of defects, scrap, rework,
          and other configurable manufacturing costs.
        </p>
      </section>

      <section className="dashboard-grid">
        <div className="dashboard-card">
          <span>Total Production</span>
          <strong>15,076,876</strong>
          <small>Total parts in the production dataset</small>
        </div>

        <div className="dashboard-card">
          <span>Estimated Defects</span>
          <strong>753,844</strong>
          <small>Based on the configurable 5% demo assumption</small>
        </div>

        <div className="dashboard-card">
          <span>Scrap + Rework</span>
          <strong>₹263.85M</strong>
          <small>Estimated configurable economic impact</small>
        </div>

        <div className="dashboard-card">
          <span>Analysis Status</span>
          <strong>Ready</strong>
          <small>Economic model available</small>
        </div>
      </section>

      <section className="system-overview">
        <div>
          <span className="section-label">IMPORTANT</span>

          <h2>Configurable Economic Model</h2>

          <p>
            These values are estimates based on configurable assumptions and
            should not be interpreted as actual financial losses.
          </p>
        </div>
      </section>
    </main>
  );
}

export default Economics;