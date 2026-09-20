function StatCard({ label, value, description, icon, trend }) {
  return (
    <div className="dashboard-card stat-card">
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: "12px",
        }}
      >
        <span>{label}</span>

        {icon && (
          <div
            style={{
              width: "34px",
              height: "34px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              borderRadius: "8px",
              background: "var(--accent-soft)",
              color: "var(--accent)",
            }}
          >
            {icon}
          </div>
        )}
      </div>

      <strong>{value}</strong>

      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "8px",
          marginTop: "7px",
        }}
      >
        <small>{description}</small>

        {trend && (
          <small
            style={{
              color: trend.type === "positive" ? "var(--success)" : "var(--warning)",
              fontWeight: 600,
            }}
          >
            {trend.label}
          </small>
        )}
      </div>
    </div>
  );
}

export default StatCard;