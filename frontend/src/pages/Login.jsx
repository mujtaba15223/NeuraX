import { useState } from "react";
import { LockKeyhole, UserRound, Factory } from "lucide-react";
import { loginEmployee } from "../services/api";

function Login({ onLogin }) {
  const [employeeId, setEmployeeId] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      const result = await loginEmployee(
        employeeId.trim(),
        password
      );

      sessionStorage.setItem("industrial_logged_in", "true");
      sessionStorage.setItem(
        "industrial_employee_id",
        result.employee_id
      );

      if (onLogin) {
        onLogin();
      }
    } catch (err) {
      setError(
        err.message || "Invalid Employee ID or Password."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-brand">
          <div className="login-logo">
            <Factory size={28} />
          </div>

          <span className="header-label">
            INDUSTRIAL OPERATIONS
          </span>

          <h1>Decision Intelligence Center</h1>

          <p>
            Secure employee access to industrial
            decision-support systems.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="login-field">
            <label htmlFor="employee-id">
              Employee ID
            </label>

            <div className="login-input-wrapper">
              <UserRound size={18} />

              <input
                id="employee-id"
                type="text"
                value={employeeId}
                onChange={(event) =>
                  setEmployeeId(event.target.value)
                }
                placeholder="Enter employee ID"
                autoComplete="username"
                required
                disabled={loading}
              />
            </div>
          </div>

          <div className="login-field">
            <label htmlFor="employee-password">
              Password
            </label>

            <div className="login-input-wrapper">
              <LockKeyhole size={18} />

              <input
                id="employee-password"
                type="password"
                value={password}
                onChange={(event) =>
                  setPassword(event.target.value)
                }
                placeholder="Enter password"
                autoComplete="current-password"
                required
                disabled={loading}
              />
            </div>
          </div>

          {error && (
            <div className="login-error">
              {error}
            </div>
          )}

          <button
            type="submit"
            className="login-button"
            disabled={loading}
          >
            {loading ? "Signing In..." : "Sign In"}
          </button>
        </form>

        <div className="login-footer">
          Authorized employee access only
        </div>
      </div>
    </div>
  );
}

export default Login;