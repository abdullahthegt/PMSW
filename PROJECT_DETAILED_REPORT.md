# Automotive DSS Semester Project - Detailed Status & Evaluation Report

## 1. Overview
This document describes the current implementation and evaluation status of the Automotive Decision Support System (DSS) prototype built as a semester project.

- Project type: Proof-of-concept (POC)
- Tech stack: Python, SQLAlchemy, Streamlit, Faker, pandas, NumPy, SciPy
- Primary scope: Synthetic data generation, velocity forecasting, resource load analysis, interactive dashboard

## 2. Currently implemented functionality

### 2.1 Database seeding (seeder.py)
- `DatabaseSeeder.seed_all()` performs:
  - `seed_teams` (3 default teams)
  - `seed_team_members` (per team members, skill/role etc.)
  - `seed_sprints` (per-team sprints, planned/actual velocity)
  - `seed_tasks` (task backlog, assignments)
  - `seed_resource_metrics` (snapshot metrics)

- `reset_database()` drops and recreates tables via `Base.metadata.drop_all` and `create_all`.
- Run commands:
  - `python seeder.py reset`
  - `python seeder.py seed`

### 2.2 Velocity prediction module
- File: `src/modules/velocity_predictor.py`
- Core stats:
  - Baseline velocity: mean of last lookback sprints
  - Volatility: std deviation over lookback
  - Trend: linear regression slope
- Predictions:
  - `predict_velocity(confidence_level)`: point estimate + CI
  - `get_safe_velocity_estimate`: lower bound for risk tolerance
  - `estimate_sprint_completion_probability`: probabilistic utility
- Visuals:
  - `plot_velocity_forecast`
  - `plot_probability_distribution`

### 2.3 Resource allocation module
- File: `src/modules/resource_load_analyzer.py`
- Task/Team modeling includes:
  - Required skill inference by task type/ASIL/ASPICE
  - Per-member capacity, efficiency, assignment logic
  - Overload tracking and bottleneck analysis
- Allocation algorithm
  - Greedy best-fit and WSJF sorting
  - Feasibility flag and bottleneck reason
  - Summary metrics: assignment rate, feasibility rate

### 2.4 Streamlit UI
- File: `app.py`
- Tabs & features:
  - 1) Velocity forecasting
  - 2) Resource analysis
  - 3) Data explorer and export
- Configuration sliders for dataset size and team parameters
- Buttons for regeneration and cache resets

## 3. Evaluation criteria coverage

### 3.1 A. Verification (Internal Consistency)
Project currently supports:
- Safe skill matching (`can_handle_task` + required skill list)
- Assignment capacity checks (`assign_task` blocks >available capacity)
- Bottleneck reporting (skill gaps + overloads)
- Feasibility metrics in output

### 3.2 B. Validation (Predictive Utility)
Project currently supports:
- Forecasted 80% CI for next sprint in `VelocityPredictor`
- Volatility and trend aware confidence intervals
- `estimate_sprint_completion_probability` meets predictive currency

## 4. Required enhancements to fully certify criteria

### 4.1 Add explicit verification harness
- Implement a test / function to compute:
  - `constraint_satisfaction_rate` = 100 * (safe_assigned_tasks / total_tasks)
  - checks that ASIL C/D tasks require Functional Safety skill
  - checks no assignment overload unless marked unsafe
- Example method in `resource_load_analyzer` or dedicated test file.

### 4.2 Add validation backtesting harness
- Use historical data generation in 20-run scenario:
  - train on first 17 sprints
  - predict sprint 18 with 80% CI
  - compare actual sprint 18 with lower/upper bounds
- Record success ratio over multiple iterations
- Add script: `backtest_velocity.py` or tests in `tests/test_velocity.py`

### 4.3 Add metrics logging for reporting
- Constraint satisfaction rate
- CI coverage rate
- feasibility rate
- these become final grade evidence

## 5. Current status judgment

- Core POC requirement: met
- For full “project evaluation / grading” readiness: additional measurement code + tests needed
- Implementation maturity: > core prototype, moderate production traces

## 6. Quick demo commands
- Seed data:
  - `python seeder.py reset`
  - `python seeder.py seed`
- Start dashboard:
  - `streamlit run app.py --server.port 8501`
- Open in browser:
  - `http://localhost:8501`

## 7. Presented to professor: next steps
- Enhance with fixed evaluation script and test cases
- Add short 1-page summary with metrics & evidence
- Optionally add `Makefile` or `run_tasks.sh` to automate verification and report generation

---

File created by assistant in project root: `PROJECT_DETAILED_REPORT.md`