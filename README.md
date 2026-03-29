# Automotive Decision Support System (DSS)

A Python-based Decision Support Tool for Agile Project Management in Automotive Engineering. Addresses the "Agile-Safety Paradox" through synthetic data generation, probabilistic velocity forecasting, and heuristic resource allocation.

## 📋 Overview

This tool synthesizes concepts from:
- **Agile Project Management** - Sprint planning and velocity tracking
- **Operations Research** - Resource-Constrained Project Scheduling (RCPSP)
- **Stochastic Simulation** - Monte Carlo methods for risk analysis
- **Automotive Standards** - ISO 26262, ASPICE compliance

### Key Features

✅ **Synthetic Data Generation** - Creates realistic automotive project datasets  
✅ **Sprint Velocity Forecasting** - Predicts team capacity with confidence intervals  
✅ **Resource Load Analysis** - Allocates tasks while respecting skill constraints  
✅ **Interactive Dashboard** - Streamlit-based web interface for decision-making  

## 🏗️ Architecture

```
automotive-dss/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── src/
│   ├── data/
│   │   ├── synthetic_data_generator.py    # SDG module
│   │   └── __init__.py
│   ├── modules/
│   │   ├── velocity_predictor.py          # Velocity forecasting
│   │   ├── resource_load_analyzer.py      # Resource allocation
│   │   └── __init__.py
│   └── __init__.py
├── tests/
└── README.md
```

## 🚀 Quick Start

### Installation

1. Clone the repository
```bash
cd automotive-dss
```

2. Create a Python virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

### Running the Application

```bash

```

The application will open in your default browser at `http://localhost:8501`

## 📊 Main Modules

### 1. Synthetic Data Generator (`src/data/synthetic_data_generator.py`)

Generates realistic automotive project datasets with:
- **Team Members**: Roles (Developer, Tester, Architect, etc.), seniority, skills
- **Product Backlog**: Tasks with ASPICE levels, ASIL criticality, dependencies
- **Historical Sprints**: Past velocity data with risk events
- **Risk Register**: Identified project risks with probabilities and impacts

**Key Features:**
- Respects V-Model task dependencies
- Statistical fidelity (Gamma distribution for story points)
- Realistic effort estimation based on ASIL levels
- Reproducible with seed control

**Example Usage:**
```python
from src.data.synthetic_data_generator import SyntheticDataGenerator

generator = SyntheticDataGenerator(seed=42)
dataset = generator.generate_complete_project_dataset(
    project_name="Adaptive Cruise Control",
    team_size=12,
    num_stories=30,
    num_historical_sprints=10
)
```

### 2. Velocity Predictor (`src/modules/velocity_predictor.py`)

Implements probabilistic velocity forecasting addressing the "Flaw of Averages":

$$V_{sprint} \sim \mathcal{N}(\mu, \sigma^2)$$

**Key Features:**
- Rolling average for baseline velocity
- Standard deviation for volatility quantification
- Trend analysis using linear regression
- Confidence intervals (80%, 90%)
- Safety velocity estimation for risk-averse planning

**Methods:**
- `predict_velocity(confidence_level)` - Forecast with confidence interval
- `estimate_sprint_completion_probability(planned_sp)` - Success probability
- `get_safe_velocity_estimate()` - Conservative velocity
- `analyze_sprint_health()` - Team stability assessment
- `generate_velocity_report()` - Planning options analysis

**Example Usage:**
```python
from src.modules.velocity_predictor import VelocityPredictor

predictor = VelocityPredictor(historical_data, lookback_sprints=3)

# Get forecast
prediction = predictor.predict_velocity(confidence_level=0.80)
print(f"Safe velocity: {prediction['lower_bound']} SP")

# Check if planned work is feasible
prob = predictor.estimate_sprint_completion_probability(planned_sp=45)
print(f"Success probability: {prob:.1%}")
```

### 3. Resource Load Analyzer (`src/modules/resource_load_analyzer.py`)

Solves the Multi-Mode Resource-Constrained Project Scheduling Problem (MRCPSP):

**Key Features:**
- Skill-based task allocation (not fungible resources)
- Heuristic-based assignment (Weighted Shortest Job First)
- Bottleneck detection (critical resources, skill gaps)
- Load balancing with overload warnings

**Methods:**
- `allocate_resources()` - Greedy allocation with feasibility check
- `get_allocation_summary()` - High-level metrics
- `suggest_rebalancing()` - Actionable recommendations
- `analyze_bottlenecks()` - Identifies constraints

**Example Usage:**
```python
from src.modules.resource_load_analyzer import ResourceLoadAnalyzer

analyzer = ResourceLoadAnalyzer(team_df, tasks_df)
result = analyzer.allocate_resources()

# Check feasibility
if result["feasibility"]:
    print("✓ Allocation is feasible")
else:
    print("✗ Resource constraints violated")
    for suggestion in analyzer.suggest_rebalancing():
        print(f"  {suggestion}")
```

## 📈 Interactive Dashboard Features

### Tab 1: Velocity Forecasting
- Historical velocity trend with uncertainty cone
- Team health assessment (stability, trend, risk level)
- Planning options analysis (30-55 story points)
- Probability distribution visualization
- Confidence interval guidance

### Tab 2: Resource Analysis
- Team member workload visualization
- Skill coverage analysis
- Bottleneck identification
- Task allocation table with status
- Rebalancing recommendations

### Tab 3: Data Explorer
- View/download team member data
- View/download product backlog
- View/download historical sprint data
- View/download risk register
- CSV export capability

## 🎯 Use Case: Adaptive Cruise Control (ACC) Project

**Scenario**: Team planning Sprint 12 with 45 story points

### Step 1: Velocity Analysis
- Historical average: 42 SP
- Volatility: ±10 SP
- Safe velocity (80% confidence): 38 SP
- **Insight**: 45 SP is risky (only 40% success probability)

### Step 2: Resource Allocation
- Allocate 35 tasks across 12 team members
- Safety Manager is a bottleneck (limited availability)
- No developers for "Hardware Integration" skill
- **Insight**: Scope reduction or resource negotiation needed

### Step 3: Decision Support
- Remove 5 low-priority SP → 40 SP (safer)
- Negotiate more Safety Manager hours
- Cross-train one developer in Hardware Integration
- **Outcome**: 80% success probability

## 🔬 Theoretical Foundation

### Problem Statement
Agile methodologies designed for unregulated software conflict with automotive safety standards (ISO 26262, ASPICE). This creates:
1. **Sprint Planning Complexity** - Velocity volatility and hidden compliance work
2. **Resource Allocation Challenges** - Non-fungible specialists and shared resources
3. **Data Scarcity** - No public automotive project datasets

### Solution Approach
1. **Synthetic Data Generation** - Create realistic datasets respecting automotive constraints
2. **Stochastic Modeling** - Replace single-point estimates with distributions
3. **Heuristic Optimization** - Practical allocation algorithms for real-time planning

## 📚 References

Based on research spanning:
- Agile in Automotive (literature review on challenges)
- ISO 26262 (Functional Safety)
- Automotive SPICE (ASPICE) processes
- Operations Research (RCPSP, scheduling)
- Project Management (Monte Carlo simulation)

## 🛠️ Technology Stack

- **Python 3.8+** - Core language
- **Streamlit** - Interactive web interface
- **Pandas** - Data manipulation
- **NumPy/SciPy** - Statistical calculations
- **Matplotlib/Seaborn** - Visualizations

## 📝 Configuration

The application supports dynamic configuration:
- Project name and scope
- Team size and composition
- Backlog size
- Historical sprint data range
- Confidence levels for forecasting

All parameters are configurable through the Streamlit sidebar.

## ⚠️ Limitations & Future Work

**Current Limitations:**
- Risk Simulator not yet implemented (simplified approach)
- Basic greedy heuristic for allocation (no complex optimization)
- Single-sprint planning horizon

**Future Enhancements:**
- Monte Carlo risk simulation (Section 5.4)
- Genetic algorithms for optimal allocation
- Multi-sprint roadmap planning
- Integration with Jira/Azure DevOps APIs
- Real automotive project data calibration

## 📄 License

This project is for research and educational purposes.

## 👥 Authors

Built for automotive engineering teams navigating the Agile-Safety Paradox.

---

**Version**: 1.0.0  
**Last Updated**: January 2026
