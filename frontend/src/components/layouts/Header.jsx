import { useEffect, useState } from "react";
import {
  Activity,
  Bell,
  CheckCircle2,
  XCircle,
  UserRound,
} from "lucide-react";
import { getHealth } from "../../services/api";

function Header() {
  const [health, setHealth] = useState(null);
  const [notificationsOpen, setNotificationsOpen] = useState(false);

  const employeeId =
    sessionStorage.getItem("industrial_employee_id") || "Employee";

  useEffect(() => {
    let active = true;

    const checkHealth = async () => {
      try {
        const result = await getHealth();

        if (active) {
          setHealth(result);
        }
      } catch {
        if (active) {
          setHealth(null);
        }
      }
    };

    checkHealth();

    const interval = window.setInterval(checkHealth, 30000);

    return () => {
      active = false;
      window.clearInterval(interval);
    };
  }, []);

  const serverOnline = health?.status === "healthy";

  return (
    <header className="header">
      <div>
        <span className="header-label">
          INDUSTRIAL OPERATIONS
        </span>

        <h1>Decision Intelligence Center</h1>
      </div>

      <div className="header-actions">
        <div
          className={`live-status ${
            serverOnline ? "online" : "offline"
          }`}
        >
          <span className="status-dot" />

          <Activity size={17} />

          <span>
            {health ? "Live Server" : "Server Offline"}
          </span>
        </div>

        <div className="employee-badge">
          <UserRound size={16} />

          <div>
            <span>Employee</span>
            <strong>{employeeId}</strong>
          </div>
        </div>

        <button
          className={`icon-button ${
            notificationsOpen ? "active" : ""
          }`}
          aria-label="Notifications"
          aria-expanded={notificationsOpen}
          onClick={() =>
            setNotificationsOpen((open) => !open)
          }
        >
          <Bell size={19} />

          <span className="notification-dot" />
        </button>

        {notificationsOpen && (
          <div
            className="notification-panel"
            role="status"
          >
            <div className="notification-panel-header">
              <strong>System status</strong>

              <span>
                {serverOnline
                  ? "Live"
                  : "Unavailable"}
              </span>
            </div>

            <div className="notification-item">
              {serverOnline ? (
                <CheckCircle2 size={17} />
              ) : (
                <XCircle size={17} />
              )}

              <div>
                <strong>
                  {serverOnline
                    ? "Backend connected"
                    : "Backend unavailable"}
                </strong>

                <small>
                  {serverOnline
                    ? "Inspection and decision analysis are ready."
                    : "Start FastAPI to enable live analysis."}
                </small>
              </div>
            </div>

            {serverOnline && (
              <div className="notification-meta">
                <span>Model 1</span>

                <strong>
                  {health.model1_loaded
                    ? "Loaded"
                    : "Missing"}
                </strong>

                <span>Model 2</span>

                <strong>
                  {health.model2_loaded
                    ? "Loaded"
                    : "Missing"}
                </strong>
              </div>
            )}
          </div>
        )}
      </div>
    </header>
  );
}

export default Header;