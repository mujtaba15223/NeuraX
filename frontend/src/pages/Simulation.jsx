import { useEffect, useState } from "react";
import { RefreshCw, Play, AlertTriangle } from "lucide-react";

import ScenarioControls from "../components/simulation/ScenarioControls";
import SimulationResults from "../components/simulation/SimulationResults";
import BeforeAfter from "../components/simulation/BeforeAfter";
import ImpactComparison from "../components/simulation/ImpactComparison";
import API_BASE_URL from "../config/api";

function Simulation() {
  const [analysis, setAnalysis] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState("");

  const fetchAnalysis = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await fetch(`${API_BASE_URL}/analysis`);

      if (!response.ok) {
        throw new Error("Failed to load production analysis");
      }

      const data = await response.json();
      setAnalysis(data);
    } catch (err) {
      setError(err.message || "Unable to connect to backend");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalysis();
  }, []);

  const runSimulation = ({ station, scenario, improvement }) => {
    if (!analysis) {
      return;
    }

    setRunning(true);
    setError("");

    const processAnalysis =
      analysis?.process?.process_analysis || {};

    const stationData =
      processAnalysis[station] || {};

    const baselineQueue =
      Number(stationData.avg_queue ?? 0);

    const baselineUtilization =
      Number(stationData.avg_utilization ?? 0);

    const baselineThroughput =
      Number(
        analysis?.production_impact?.average_parts_per_hour ??
          analysis?.production?.average_parts_per_hour ??
          0
      );

    const improvementFactor =
      Number(improvement) / 100;

    let projectedQueue = baselineQueue;
    let projectedUtilization = baselineUtilization;
    let projectedThroughput = baselineThroughput;

    if (scenario === "Reduce Queue Time") {
      projectedQueue =
        baselineQueue * (1 - improvementFactor);

      projectedThroughput =
        baselineThroughput *
        (1 + improvementFactor * 0.25);
    }

    if (scenario === "Increase Capacity") {
      projectedUtilization =
        baselineUtilization *
        (1 - improvementFactor * 0.5);

      projectedThroughput =
        baselineThroughput *
        (1 + improvementFactor * 0.5);
    }

    if (scenario === "Reduce Utilization") {
      projectedUtilization =
        baselineUtilization *
        (1 - improvementFactor);

      projectedThroughput =
        baselineThroughput *
        (1 + improvementFactor * 0.2);
    }

    if (scenario === "Reduce Cycle Time") {
      projectedThroughput =
        baselineThroughput *
        (1 + improvementFactor * 0.4);

      projectedQueue =
        baselineQueue *
        (1 - improvementFactor * 0.3);
    }

    const baselineImpact =
      Number(
        analysis?.impact?.total_estimated_impact ??
          analysis?.production_impact?.total_estimated_impact ??
          0
      );

    const throughputGain =
      projectedThroughput - baselineThroughput;

    const estimatedSavings =
      Math.max(0, throughputGain) * 250;

    const projectedImpact =
      Math.max(
        0,
        baselineImpact - estimatedSavings
      );

    setResult({
      station,
      scenario,
      improvement: Number(improvement),

      before: {
        queue: baselineQueue,
        utilization: baselineUtilization,
        throughput: baselineThroughput,
      },

      after: {
        queue: projectedQueue,
        utilization: projectedUtilization,
        throughput: projectedThroughput,
      },

      baseline: {
        throughput: baselineThroughput,
        queue: baselineQueue,
        impact: baselineImpact,
      },

      simulated: {
        throughput: projectedThroughput,
        queue: projectedQueue,
        impact: projectedImpact,
      },

      estimated_savings: estimatedSavings,
    });

    setRunning(false);
  };

  if (loading) {
    return (
      <div className="page-container">
        <div className="page-header">
          <div>
            <span className="header-label">
              WHAT-IF SIMULATION
            </span>

            <h1>Production Simulation</h1>

            <p>
              Test process improvements before applying
              them to production.
            </p>
          </div>
        </div>

        <div className="dashboard-card">
          <div className="empty-state">
            <RefreshCw
              className="spin"
              size={28}
            />

            <p>
              Loading production model...
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (error && !analysis) {
    return (
      <div className="page-container">
        <div className="page-header">
          <div>
            <span className="header-label">
              WHAT-IF SIMULATION
            </span>

            <h1>Production Simulation</h1>

            <p>
              Test process improvements before applying
              them to production.
            </p>
          </div>
        </div>

        <div className="dashboard-card">
          <div className="empty-state">
            <AlertTriangle size={30} />

            <h3>
              Simulation Unavailable
            </h3>

            <p>{error}</p>

            <button
              className="action-button"
              onClick={fetchAnalysis}
            >
              <RefreshCw size={16} />
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <span className="header-label">
            WHAT-IF SIMULATION
          </span>

          <h1>Production Simulation</h1>

          <p>
            Test process improvements and estimate their
            effect on throughput, queue pressure, and
            economic impact.
          </p>
        </div>

        <button
          className="action-button"
          onClick={fetchAnalysis}
        >
          <RefreshCw size={16} />
          Refresh Model
        </button>
      </div>

      <div className="dashboard-card">
        <div className="card-header">
          <div>
            <span className="header-label">
              SCENARIO BUILDER
            </span>

            <h3>
              Configure What-If Scenario
            </h3>
          </div>

          <Play size={22} />
        </div>

        <ScenarioControls
          onRun={runSimulation}
        />

        {running && (
          <div className="simulation-running">
            <RefreshCw
              className="spin"
              size={18}
            />

            Running simulation...
          </div>
        )}
      </div>

      <SimulationResults
        result={result}
      />

      {result && (
        <>
          <BeforeAfter
            before={result.before}
            after={result.after}
          />

          <ImpactComparison
            baseline={result.baseline}
            simulated={result.simulated}
          />
        </>
      )}

      <div className="dashboard-card causality-warning">
        <div className="warning-icon">
          <AlertTriangle size={20} />
        </div>

        <div>
          <strong>
            Simulation Assumption
          </strong>

          <p>
            What-if results are modeled estimates based
            on configurable improvement assumptions.
            They should be validated with real production
            experiments before operational decisions are
            made.
          </p>
        </div>
      </div>
    </div>
  );
}

export default Simulation;