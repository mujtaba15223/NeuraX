import { useState } from "react";
import { FlaskConical, Play } from "lucide-react";

function ScenarioControls({ onRun, running = false }) {
  const [station, setStation] = useState("Drilling");
  const [scenario, setScenario] = useState(
    "Reduce Queue Time"
  );
  const [improvement, setImprovement] = useState(20);

  function handleRun() {
    onRun?.({
      station,
      scenario,
      improvement: Number(improvement),
    });
  }

  return (
    <div className="dashboard-card">
      <div className="card-header">
        <div>
          <span className="header-label">
            WHAT-IF SIMULATION
          </span>

          <h3>Scenario Controls</h3>
        </div>

        <FlaskConical size={22} />
      </div>

      <div
        style={{
          display: "grid",
          gap: "18px",
        }}
      >
        <div>
          <label
            htmlFor="simulation-station"
            style={{
              display: "block",
              marginBottom: "8px",
              fontWeight: 600,
            }}
          >
            Production Station
          </label>

          <select
            id="simulation-station"
            value={station}
            onChange={(event) =>
              setStation(event.target.value)
            }
            style={{
              width: "100%",
              padding: "11px 12px",
              borderRadius: "8px",
              border: "1px solid #263442",
              background: "#0b1118",
              color: "inherit",
            }}
          >
            <option value="Drilling">
              Drilling
            </option>

            <option value="Milling">
              Milling
            </option>

            <option value="Assembly">
              Assembly
            </option>
          </select>
        </div>

        <div>
          <label
            htmlFor="simulation-scenario"
            style={{
              display: "block",
              marginBottom: "8px",
              fontWeight: 600,
            }}
          >
            Intervention
          </label>

          <select
            id="simulation-scenario"
            value={scenario}
            onChange={(event) =>
              setScenario(event.target.value)
            }
            style={{
              width: "100%",
              padding: "11px 12px",
              borderRadius: "8px",
              border: "1px solid #263442",
              background: "#0b1118",
              color: "inherit",
            }}
          >
            <option value="Reduce Queue Time">
              Reduce Queue Time
            </option>

            <option value="Increase Capacity">
              Increase Capacity
            </option>

            <option value="Reduce Utilization">
              Reduce Utilization
            </option>

            <option value="Reduce Cycle Time">
              Reduce Cycle Time
            </option>
          </select>
        </div>

        <div>
          <label
            htmlFor="simulation-improvement"
            style={{
              display: "block",
              marginBottom: "8px",
              fontWeight: 600,
            }}
          >
            Expected Improvement
          </label>

          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "14px",
            }}
          >
            <input
              id="simulation-improvement"
              type="range"
              min="5"
              max="50"
              step="5"
              value={improvement}
              onChange={(event) =>
                setImprovement(
                  Number(event.target.value)
                )
              }
              style={{
                flex: 1,
              }}
            />

            <strong
              style={{
                minWidth: "52px",
                textAlign: "right",
              }}
            >
              {improvement}%
            </strong>
          </div>

          <small>
            Simulated improvement applied to the
            selected intervention.
          </small>
        </div>

        <button
          className="primary-button"
          onClick={handleRun}
          disabled={running}
        >
          {running ? (
            <>
              <Play size={17} className="spin" />
              Running Simulation...
            </>
          ) : (
            <>
              <Play size={17} />
              Run Simulation
            </>
          )}
        </button>
      </div>
    </div>
  );
}

export default ScenarioControls;