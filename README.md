# Visual Inspection & Defect Root-Cause Assistant

**An industrial decision-support system that connects visual defect detection to manufacturing-process data, so a single image doesn't just answer "is this defective?" — it triggers an investigation into why, where the line is constrained, what it's costing, and what to do about it.**

---
## 1. The Problem

A computer-vision model can tell a factory:

> "This product is defective."

That's the easy part. What a manufacturing engineer actually needs is:

- What is wrong, and where?
- What process conditions were unusual when it happened?
- Is this a one-off or a symptom of a bottleneck?
- What is it costing us?
- What should we investigate first?
- If we fix it, what changes?

Most systems answer one of these questions in isolation — a defect classifier, or a KPI dashboard, or a quality log — and leave the engineer to manually stitch the rest together. We built a system that stitches it together automatically.

---

## 2. What We're Building

A pipeline that takes a product image and a manufacturing-process snapshot, and produces an evidence-backed diagnosis:

```
Product Image
     │
     ▼
Defect Detection (type, location, severity)
     │
     ▼
Process Context (station, utilization, queue, cycle time)
     │
     ▼
Root-Cause Engine → likely contributing factors
     │
     ▼
Bottleneck Engine → capacity constraints
     │
     ▼
Economic Engine → cost / throughput impact
     │
     ▼
Recommendation Engine → what to investigate
     │
     ▼
What-If Simulation → what happens if we change it
```

The core design decision: **this is a modular decision-support system, not a single end-to-end model.** Vision, process analytics, root-cause reasoning, and economics are separate, independently-testable components that pass structured evidence to each other. That keeps every stage explainable and lets us swap or improve one piece without touching the rest.

---

## 3. Design Principles (and where we're deliberately being careful)

- **No blind causality claims.** The public vision dataset and the public manufacturing-process datasets come from different sources — they don't share real product-level identifiers. So the system never says "Machine X caused this defect." It says "these process variables were abnormal in the same window as this defect pattern," reports a confidence level, and is explicit that this is *association*, not proven causation.
- **A controlled data-association layer, not a merge.** We connect vision output and process data through a unified schema (product/batch/SKU/station/timestamp) built for a realistic simulated factory, rather than pretending two unrelated public datasets describe the same physical products.
- **Evidence-first, always.** Every recommendation the system produces cites the specific process variables and their deviation from baseline — never a black-box "trust me."
- **Dataset-aware, not model-first.** We're inspecting Model 1 and Model 2 (below) before locking in a vision architecture, rather than picking a trendy model and retrofitting a use case.

---

## 4. Why Bottleneck Detection Isn't Just "High Utilization"

A station running at 95% utilization is not automatically the constraint — a well-buffered line can run one station hot without it being the bottleneck. We combine several signals instead of one:

- Utilization
- Queue length ahead of the station
- Waiting time
- Cycle-time drift from baseline
- Capacity imbalance vs. upstream/downstream stations
- Measured throughput impact

The exact weighting will be calibrated against the manufacturing datasets rather than fixed a priori.

---

## 5. Data

### 5.1 Manufacturing process data

**Model 1 — simple line** (Raw Material → Drilling → Milling → Assembly → Finished Product)
Used as a clean baseline for validating throughput, utilization, and bottleneck logic before adding complexity. Key variables: demand, entities in/out, value-added time, per-stage queue time, storage time, per-stage utilization.

**Model 2 — complex line** (Blanking → Presses → Cells → Warehouse → Painting → Quality → Finished Product)
Our primary scenario: multiple SKUs, multiple stations, material handling, and quality inspection — closer to a real factory, with SKU-specific cycle times and station imbalance to exercise the full pipeline.

### 5.2 Visual inspection data

We're evaluating two candidate datasets and will pick based on fit with the demo scenario, not use both by default:

- **MVTec AD** — general industrial anomaly detection across multiple object/texture categories.
- **NEU Surface Defect Dataset** — steel surface defects; strong fit for classification + localization.

### 5.3 Unified schema

A shared record ties inspection results to process state:

```
product_id, batch_id, sku, timestamp,
defect_type, defect_location, severity, confidence,
station, utilization, queue_time, cycle_time, waiting_time
```

This is what makes the root-cause engine possible without overstating what the raw datasets can prove.

---

## 6. System Architecture

```
                    Visual Dataset
                          │
                          ▼
                  Computer Vision AI
                          │
           defect type / location / severity
                          │
Manufacturing ──────►  Unified Data Layer  ◄────── Manufacturing
   Model 1                    │                        Model 2
                               ▼
                     Process Analytics Engine
                               │
             ┌─────────────────┼─────────────────┐
             ▼                 ▼                  ▼
       Root-Cause         Bottleneck         Process Drift
         Engine             Engine              Engine
             │                 │                  │
             └─────────────────┼──────────────────┘
                               ▼
                       Economic Analysis
                               │
                               ▼
                     Recommendation Engine
                               │
                               ▼
                      What-If Simulation
                               │
                               ▼
                       React Dashboard (FastAPI backend)
```

---

## 7. Engines, Briefly

| Engine | Input | Output |
|---|---|---|
| **Process Analytics** | Raw process logs | Throughput, utilization, queue time, cycle time, waiting time, WIP |
| **Root-Cause** | Defect + process context | Ranked "likely contributing factors" with supporting evidence |
| **Bottleneck** | Multi-station process metrics | Which station is the current constraint, and why |
| **Economic** | Defect + bottleneck output | Scrap/rework cost, estimated throughput/revenue impact |
| **Recommendation** | All of the above | A specific, evidence-cited investigation suggestion |
| **What-If Simulation** | User-proposed change (e.g. "cut Cell 2 cycle time 10%") | Projected throughput, queue, and cost delta |

Example of the output style we're aiming for — not "Cell 2 is broken," but:

```
Likely contributing factors (Cell 2, Batch 47, SKU-3):
1. Utilization 22% above 30-day baseline
2. Queue time trending upward over last 6 batches
3. Cycle time deviated +14% from baseline
Defect frequency for this SKU increased over the same window.
→ Evidence-based association, not confirmed causation. Recommend investigating Cell 2 process stability.
```

---

## 8. Dashboard Views

- **Main** — production status, defect rate, throughput, current bottleneck, estimated economic impact at a glance.
- **Inspection** — image, defect type, location, severity, confidence.
- **Production** — per-station utilization, queue, cycle time, flagged bottleneck.
- **Root-Cause** — defect → associated stage → abnormal variables → evidence.
- **Economic** — scrap/rework/downtime cost, throughput impact, scenario comparison.
- **What-If** — current state vs. simulated state, side by side.

## 9. Tech Stack

| Layer               | Technology                                    |
| ------------------- | --------------------------------------------- |
| **Language**        | Python                                        |
| **Computer Vision** | OpenCV, PyTorch, YOLO                         |
| **ML / AI**         | XGBoost, scikit-learn, Isolation Forest, SHAP |
| **Data Analytics**  | Pandas, NumPy                         |
| **Backend**         | FastAPI                                       |
| **Frontend**        | React                                         |
| **Database**        | CSV → SQLite / PostgreSQL                     |
| **Visualization**   | Rechart                            |
| **Development**     | Jupyter, VS Code, Git, GitHub                 |
| **Deployment**      | Docker / Cloud: versel                         |

### AI Pipeline

```text
YOLO
 ↓
Defect Detection
 ↓
Isolation Forest + XGBoost
 ↓
Process Anomaly & Root-Cause Analysis
 ↓
SHAP Explainability
 ↓
Bottleneck + Impact Analysis
 ↓
What-If Simulation
 ↓
Recommendations
```

**Design principle:** Use specialized AI/ML models for each industrial task instead of relying on a single model for the entire system.


## 10. Project Structure

```
industrial-defect-root-cause-ai/
├── data/
│   ├── raw/{model1, model2, images}/
│   ├── processed/{model1, model2, images}/
│   └── unified/{products,batches,production_events,inspections,process_conditions}.csv
├── ai/
│   ├── vision/          # dataset, preprocessing, train, predict, model
│   ├── anomaly/         # drift_detection, anomaly_detection
│   └── root_cause/      # feature_analysis, correlation, root_cause_engine, explanation
├── analytics/           # throughput, cycle_time, utilization, queue, bottleneck, wip, profitability
├── simulation/          # what_if, production_simulator, scenarios
├── backend/
│   ├── main.py
│   ├── api/             # inspection, production, bottleneck, root_cause, recommendations, simulation
│   ├── services/
│   ├── database/
│   └── utils/
├── frontend/
│   └── src/{components, pages, services, App.jsx}
├── notebooks/           # exploration + analysis notebooks
├── tests/
└── docs/                # architecture, data_dictionary, methodology, api, demo_scenario
```

---

## 11. End-to-End Flow (Demo Scenario)

1. **Inspect** — a product image is scored: normal / defective, with class, location, severity, confidence.
2. **Contextualize** — the system pulls the matching SKU/batch/station/timestamp process data.
3. **Diagnose** — root-cause engine flags abnormal process variables coinciding with the defect.
4. **Locate the constraint** — bottleneck engine checks whether the associated station is a current flow constraint.
5. **Quantify impact** — economic engine estimates scrap/rework cost and throughput/revenue effect.
6. **Recommend** — an evidence-cited investigation suggestion is generated.
7. **Simulate** — the user tests a proposed fix (e.g., reduce cycle time, add capacity) and sees the projected effect before committing to it.

---

## 12. Validation Plan

- **Vision:** accuracy, precision, recall, F1, confusion matrix, and localization quality where the dataset supports it.
- **Bottleneck detection:** cross-check flagged stations against observed queue accumulation, utilization, and throughput limitation in the source data.
- **Root-cause engine:** assess whether flagged variables are genuinely associated with defect patterns, not just noise — measured against held-out batches.
- **Simulation:** compare simulated outcomes against known baseline relationships in the manufacturing datasets as a sanity check.

---

## 13. Known Limitations

Being upfront about these rather than glossing over them:

- The vision dataset and the process datasets are **not naturally linked** — any product-to-process mapping in the demo runs through a simulation/association layer we define, and that's clearly labeled as such throughout the system, not presented as ground truth.
- Root-cause output is **associative, not causal**. We treat this as a hard constraint on the UI language, not just a disclaimer buried in docs.
- Real factory cost parameters (labor rate, machine-hour cost, etc.) aren't in the public datasets, so the economic engine uses **configurable assumptions** that we'll state explicitly in the demo rather than presenting as measured fact.
- Final vision architecture is dataset-dependent and not yet locked in.

---

## 14. Roadmap

| Phase | Focus |
|---|---|
| 1 | Data understanding — inspect Model 1 & 2, clean, build data dictionary |
| 2 | Visual inspection — pick dataset, train baseline detector, add localization/severity |
| 3 | Process analytics — throughput, utilization, queue, cycle time, waiting time, WIP |
| 4 | Bottleneck engine |
| 5 | Unified data layer connecting product/batch/SKU/station/timestamp |
| 6 | Root-cause engine |
| 7 | Economic analysis |
| 8 | What-if simulation |
| 9 | Dashboard (React + FastAPI) |
| 10 | Validation and end-to-end demo |

---

## 15. Core Statement

We're building a decision-support system that connects visual product inspection with manufacturing-process intelligence — to identify defects, surface likely contributing process factors, detect production bottlenecks, quantify throughput and economic impact, and let engineers test corrective actions through what-if simulation before committing to them on the floor.

**Detect → Explain → Diagnose → Optimize → Simulate.**
