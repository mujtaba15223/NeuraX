import { useEffect, useState } from "react";
import { RefreshCw, Search, AlertTriangle } from "lucide-react";

import RootCausePanel from "../components/rootcause/RootCausePanel";
import EvidenceCard from "../components/rootcause/EvidenceCard";
import FactorRanking from "../components/rootcause/FactorRanking";
import RecommendationCard from "../components/rootcause/RecommendationCard";
import API_BASE_URL from "../config/api";

function RootCause() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchAnalysis = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await fetch(`${API_BASE_URL}/analysis`);

      if (!response.ok) {
        throw new Error("Failed to load root-cause analysis");
      }

      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(err.message || "Unable to connect to backend");
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
            <span className="header-label">ROOT CAUSE AI</span>
            <h1>Root Cause Investigation</h1>
            <p>
              Combining visual inspection evidence with manufacturing process
              signals.
            </p>
          </div>
        </div>

        <div className="dashboard-card">
          <div className="empty-state">
            <RefreshCw className="spin" size={28} />
            <p>Running root-cause analysis...</p>
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
            <span className="header-label">ROOT CAUSE AI</span>
            <h1>Root Cause Investigation</h1>
            <p>
              Combining visual inspection evidence with manufacturing process
              signals.
            </p>
          </div>
        </div>

        <div className="dashboard-card">
          <div className="empty-state">
            <AlertTriangle size={30} />
            <h3>Analysis Unavailable</h3>
            <p>{error}</p>

            <button className="action-button" onClick={fetchAnalysis}>
              <RefreshCw size={16} />
              Retry Analysis
            </button>
          </div>
        </div>
      </div>
    );
  }

  const rootCause = data?.root_cause || {};
  const processAnalysis = Array.isArray(data?.process?.analysis)
    ? data.process.analysis
    : Array.isArray(data?.process?.process_analysis)
      ? data.process.process_analysis
      : Array.isArray(data?.process_analysis)
        ? data.process_analysis
        : [];

  const evidence = rootCause.evidence || rootCause.process_evidence || {};

  const factors = processAnalysis.map((values, index) => ({
    station: values?.station || `Station ${index + 1}`,
    score: values?.score ?? values?.pressure_score ?? values?.combined_pressure ?? 0,
    queue_pressure: values?.queue_pressure ?? 0,
    utilization_pressure: values?.utilization_pressure ?? 0,
    queue: values?.avg_queue ?? values?.queue_time ?? 0,
    utilization: values?.avg_utilization ?? values?.utilization ?? 0,
    rank: values?.rank ?? index + 1,
  }));

  factors.sort((a, b) => {
    if (a.rank && b.rank) {
      return a.rank - b.rank;
    }

    return b.score - a.score;
  });

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <span className="header-label">ROOT CAUSE AI</span>
          <h1>Root Cause Investigation</h1>
          <p>
            Connect defect evidence with process conditions to identify likely
            contributing factors.
          </p>
        </div>

        <button className="action-button" onClick={fetchAnalysis}>
          <RefreshCw size={16} />
          Refresh Analysis
        </button>
      </div>

      <div className="dashboard-grid">
        <RootCausePanel data={rootCause} />

        <EvidenceCard evidence={evidence} />
      </div>

      <div className="dashboard-grid">
        <FactorRanking factors={factors} />

        <RecommendationCard
          recommendation={rootCause.recommendation}
        />
      </div>

      <div className="dashboard-card">
        <div className="card-header">
          <div>
            <span className="header-label">ANALYSIS FLOW</span>
            <h3>How the AI Reaches the Investigation Direction</h3>
          </div>

          <Search size={22} />
        </div>

        <div className="analysis-flow">
          <div className="flow-step">
            <span className="flow-number">01</span>
            <div>
              <strong>Defect Evidence</strong>
              <p>
                Visual inspection identifies the observed defect and anomaly
                signal.
              </p>
            </div>
          </div>

          <div className="flow-arrow">→</div>

          <div className="flow-step">
            <span className="flow-number">02</span>
            <div>
              <strong>Process Evidence</strong>
              <p>
                Queue pressure and utilization are analyzed across production
                stations.
              </p>
            </div>
          </div>

          <div className="flow-arrow">→</div>

          <div className="flow-step">
            <span className="flow-number">03</span>
            <div>
              <strong>Factor Ranking</strong>
              <p>
                Process stations are ranked using the combined pressure score.
              </p>
            </div>
          </div>

          <div className="flow-arrow">→</div>

          <div className="flow-step">
            <span className="flow-number">04</span>
            <div>
              <strong>Investigation Direction</strong>
              <p>
                The system recommends where engineers should investigate
                further.
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="dashboard-card causality-warning">
        <div className="warning-icon">
          <AlertTriangle size={20} />
        </div>

        <div>
          <strong>Important: Evidence-Based Hypothesis</strong>
          <p>
            The identified factor represents a likely contributing factor based
            on available process evidence. The system does not claim confirmed
            causality without controlled manufacturing validation.
          </p>
        </div>
      </div>
    </div>
  );
}

export default RootCause;