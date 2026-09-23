import {
  IndianRupee,
  Factory,
  AlertTriangle,
  TrendingDown,
  Clock3,
  PackageX,
} from "lucide-react";

import { useApi } from "../hooks/useApi";

function Economics() {
  const {
    data,
    loading,
    error,
    refresh,
  } = useApi();

  const impact =
    data?.economics ||
    data?.production_impact ||
    {};

  const production =
    data?.production || {};

  const formatNumber = (value) =>
    Number(value ?? 0).toLocaleString(
      "en-IN",
      {
        maximumFractionDigits: 2,
      }
    );

  const formatCurrency = (value) =>
    `₹${Number(value ?? 0).toLocaleString(
      "en-IN",
      {
        maximumFractionDigits: 0,
      }
    )}`;

  const totalParts = Number(
    production.total_parts ?? 0
  );

  const estimatedDefects = Number(
    impact.estimated_defective_parts ?? 0
  );

  const defectRate = Number(
    impact.assumed_defect_rate ?? 0
  );

  const scrapCost = Number(
    impact.scrap_cost ?? 0
  );

  const reworkCost = Number(
    impact.rework_cost ?? 0
  );

  const downtimeCost = Number(
    impact.downtime_cost ?? 0
  );

  const totalImpact = Number(
    impact.total_estimated_impact ?? 0
  );

  const scrapAndRework =
    scrapCost + reworkCost;

  const totalGoodParts =
    Math.max(
      0,
      totalParts - estimatedDefects
    );

  if (loading) {
    return (
      <main className="page-container">
        <section className="page-header">
          <div>
            <span className="header-label">
              PRODUCTION ECONOMICS
            </span>

            <h1>
              Loading economic model...
            </h1>

            <p>
              Calculating estimated scrap,
              rework, and downtime exposure
              from the production data.
            </p>
          </div>
        </section>

        <div className="dashboard-card">
          <div className="empty-state">
            <TrendingDown
              size={28}
              className="spin"
            />

            <p>
              Calculating production impact...
            </p>
          </div>
        </div>
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

            <h1>
              Economic model unavailable
            </h1>

            <p>{error}</p>

            <button
              className="primary-button"
              onClick={refresh}
            >
              Retry
            </button>
          </div>
        </section>
      </main>
    );
  }

  return (
    <main className="page-container">

      {/* HEADER */}
      <section className="page-header">
        <div>
          <span className="header-label">
            PRODUCTION ECONOMICS
          </span>

          <h1>
            Economic Impact
          </h1>

          <p>
            Estimate the production and economic
            exposure associated with defects,
            scrap, rework, and downtime.
          </p>
        </div>
      </section>

      {/* TOTAL IMPACT */}
      <section className="dashboard-card bottleneck-highlight">
        <div className="highlight-icon">
          <IndianRupee size={28} />
        </div>

        <div>
          <span className="header-label">
            ESTIMATED PRODUCTION IMPACT
          </span>

          <h2>
            {formatCurrency(totalImpact)}
          </h2>

          <p>
            Combined estimated exposure from
            defect-related scrap, rework, and
            configured downtime assumptions.
          </p>
        </div>

        <div className="highlight-score">
          <span>
            Estimated Defects
          </span>

          <strong>
            {formatNumber(
              estimatedDefects
            )}
          </strong>

          <small>
            {(
              defectRate * 100
            ).toFixed(2)}
            % assumed rate
          </small>
        </div>
      </section>

      {/* KEY PRODUCTION METRICS */}
      <section className="dashboard-grid">

        <div className="dashboard-card">
          <div className="card-header">
            <div>
              <span className="header-label">
                PRODUCTION VOLUME
              </span>

              <h3>
                Total Production
              </h3>
            </div>

            <Factory size={22} />
          </div>

          <div className="station-score">
            <span>
              Parts in Dataset
            </span>

            <strong>
              {formatNumber(totalParts)}
            </strong>
          </div>

          <div className="metric-row">
            <span>
              Estimated Good Parts
            </span>

            <strong>
              {formatNumber(
                totalGoodParts
              )}
            </strong>
          </div>
        </div>

        <div className="dashboard-card">
          <div className="card-header">
            <div>
              <span className="header-label">
                QUALITY EXPOSURE
              </span>

              <h3>
                Defective Parts
              </h3>
            </div>

            <PackageX size={22} />
          </div>

          <div className="station-score">
            <span>
              Estimated Defects
            </span>

            <strong>
              {formatNumber(
                estimatedDefects
              )}
            </strong>
          </div>

          <div className="metric-row">
            <span>
              Assumed Defect Rate
            </span>

            <strong>
              {(
                defectRate * 100
              ).toFixed(2)}
              %
            </strong>
          </div>
        </div>

        <div className="dashboard-card">
          <div className="card-header">
            <div>
              <span className="header-label">
                SCRAP + REWORK
              </span>

              <h3>
                Quality Cost
              </h3>
            </div>

            <TrendingDown size={22} />
          </div>

          <div className="station-score">
            <span>
              Estimated Cost
            </span>

            <strong>
              {formatCurrency(
                scrapAndRework
              )}
            </strong>
          </div>

          <div className="metric-row">
            <span>
              Scrap Cost
            </span>

            <strong>
              {formatCurrency(
                scrapCost
              )}
            </strong>
          </div>

          <div className="metric-row">
            <span>
              Rework Cost
            </span>

            <strong>
              {formatCurrency(
                reworkCost
              )}
            </strong>
          </div>
        </div>

        <div className="dashboard-card">
          <div className="card-header">
            <div>
              <span className="header-label">
                DOWNTIME EXPOSURE
              </span>

              <h3>
                Operational Cost
              </h3>
            </div>

            <Clock3 size={22} />
          </div>

          <div className="station-score">
            <span>
              Estimated Downtime Cost
            </span>

            <strong>
              {formatCurrency(
                downtimeCost
              )}
            </strong>
          </div>

          <div className="metric-row">
            <span>
              Included in total impact
            </span>

            <strong>
              YES
            </strong>
          </div>
        </div>
      </section>

      {/* COST BREAKDOWN */}
      <section className="dashboard-card">
        <div className="card-header">
          <div>
            <span className="header-label">
              COST BREAKDOWN
            </span>

            <h3>
              Estimated Economic Exposure
            </h3>
          </div>

          <IndianRupee size={22} />
        </div>

        <div className="impact-list">

          <div>
            <span>
              Scrap Cost
            </span>

            <strong>
              {formatCurrency(
                scrapCost
              )}
            </strong>
          </div>

          <div>
            <span>
              Rework Cost
            </span>

            <strong>
              {formatCurrency(
                reworkCost
              )}
            </strong>
          </div>

          <div>
            <span>
              Downtime Cost
            </span>

            <strong>
              {formatCurrency(
                downtimeCost
              )}
            </strong>
          </div>

          <div className="impact-total">
            <span>
              Total Estimated Impact
            </span>

            <strong>
              {formatCurrency(
                totalImpact
              )}
            </strong>
          </div>

        </div>
      </section>

      {/* MODEL ASSUMPTIONS */}
      <section className="dashboard-card">
        <div className="card-header">
          <div>
            <span className="header-label">
              MODEL ASSUMPTIONS
            </span>

            <h3>
              Economic Model Inputs
            </h3>
          </div>

          <AlertTriangle size={22} />
        </div>

        <div className="impact-list">

          <div>
            <span>
              Defect Rate Assumption
            </span>

            <strong>
              {(
                defectRate * 100
              ).toFixed(2)}
              %
            </strong>
          </div>

          <div>
            <span>
              Scrap Cost / Part
            </span>

            <strong>
              {formatCurrency(250)}
            </strong>
          </div>

          <div>
            <span>
              Rework Cost / Part
            </span>

            <strong>
              {formatCurrency(100)}
            </strong>
          </div>

          <div>
            <span>
              Downtime Cost / Hour
            </span>

            <strong>
              {formatCurrency(1500)}
            </strong>
          </div>

        </div>

        <small className="causality-note">
          {impact.note ||
            "These values are configurable assumptions for the demonstration model and should not be treated as actual proven financial results."}
        </small>
      </section>

      {/* DECISION INTERPRETATION */}
      <section className="dashboard-card">
        <div className="card-header">
          <div>
            <span className="header-label">
              DECISION INTERPRETATION
            </span>

            <h3>
              From Defect to Economic Impact
            </h3>
          </div>

          <TrendingDown size={22} />
        </div>

        <div className="analysis-flow">

          <div className="flow-step">
            <span className="flow-number">
              01
            </span>

            <div>
              <strong>
                Defect Volume
              </strong>

              <p>
                Estimate the number of affected
                parts using the configured defect
                rate.
              </p>
            </div>
          </div>

          <div className="flow-arrow">
            →
          </div>

          <div className="flow-step">
            <span className="flow-number">
              02
            </span>

            <div>
              <strong>
                Quality Cost
              </strong>

              <p>
                Apply configurable scrap and
                rework costs to the estimated
                defect volume.
              </p>
            </div>
          </div>

          <div className="flow-arrow">
            →
          </div>

          <div className="flow-step">
            <span className="flow-number">
              03
            </span>

            <div>
              <strong>
                Operational Cost
              </strong>

              <p>
                Include the configured downtime
                exposure associated with the
                production constraint.
              </p>
            </div>
          </div>

          <div className="flow-arrow">
            →
          </div>

          <div className="flow-step">
            <span className="flow-number">
              04
            </span>

            <div>
              <strong>
                Estimated Impact
              </strong>

              <p>
                Combine the modeled costs into
                one decision-support estimate.
              </p>
            </div>
          </div>

        </div>
      </section>

      {/* IMPORTANT WARNING */}
      <section className="dashboard-card causality-warning">
        <div className="warning-icon">
          <AlertTriangle size={20} />
        </div>

        <div>
          <strong>
            Important: Model Estimate
          </strong>

          <p>
            The displayed financial impact is an
            estimate produced from the available
            production data and configurable
            assumptions. It is not a claim of
            actual factory financial loss. Real
            production trials and validated cost
            data are required before using these
            values for operational decisions.
          </p>
        </div>
      </section>

    </main>
  );
}

export default Economics;