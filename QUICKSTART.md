"""
QUICK START GUIDE - Automotive DSS
"""

# ============================================================================
# INSTALLATION & SETUP
# ============================================================================

"""
1. VERIFY PROJECT STRUCTURE

✓ Main files:
  - app.py                      # Streamlit web application
  - example.py                  # Standalone example script
  - requirements.txt            # Python dependencies
  - README.md                   # Full documentation

✓ Source modules:
  - src/data/synthetic_data_generator.py    # Data generation
  - src/modules/velocity_predictor.py       # Velocity forecasting  
  - src/modules/resource_load_analyzer.py   # Resource allocation
  - src/modules/__init__.py
  - src/data/__init__.py
  - src/__init__.py

2. CREATE VIRTUAL ENVIRONMENT

# On Windows (PowerShell):
python -m venv venv
.\venv\Scripts\Activate.ps1

# On Windows (Command Prompt):
python -m venv venv
venv\Scripts\activate.bat

# On macOS/Linux:
python -m venv venv
source venv/bin/activate

3. INSTALL DEPENDENCIES

pip install -r requirements.txt

4. VERIFY INSTALLATION

python -c "import streamlit; import pandas; import numpy; print('✓ All imports successful')"

# ============================================================================
# RUNNING THE APPLICATION
# ============================================================================

OPTION 1: INTERACTIVE DASHBOARD (RECOMMENDED)
────────────────────────────────────────────

streamlit run app.py

This will:
- Open browser to http://localhost:8501
- Show 3-tab dashboard with:
  • Velocity Forecasting analysis
  • Resource Load analysis  
  • Data Explorer


OPTION 2: COMMAND-LINE EXAMPLE
──────────────────────────────

python example.py

This will:
- Generate synthetic data
- Run velocity analysis
- Perform resource allocation
- Print detailed results to console


# ============================================================================
# CONFIGURATION & USAGE
# ============================================================================

VELOCITY PREDICTOR MODULE
─────────────────────────

from src.modules.velocity_predictor import VelocityPredictor

predictor = VelocityPredictor(historical_sprints_df, lookback_sprints=3)

# Get velocity forecast
prediction = predictor.predict_velocity(confidence_level=0.80)
print(f"Safe velocity: {prediction['lower_bound']} SP")

# Check feasibility of planned work
prob = predictor.estimate_sprint_completion_probability(planned_sp=45)
print(f"Success probability: {prob:.1%}")

# Get team health metrics
health = predictor.analyze_sprint_health()
print(f"Team stability: {health['stability']}")

# Generate planning report
report = predictor.generate_velocity_report(planned_sp_options=[40, 45, 50])


RESOURCE LOAD ANALYZER MODULE
──────────────────────────────

from src.modules.resource_load_analyzer import ResourceLoadAnalyzer

analyzer = ResourceLoadAnalyzer(team_df, tasks_df)

# Allocate resources
result = analyzer.allocate_resources()

# Check feasibility
if result["feasibility"]:
    print("✓ Allocation is feasible")

# Get summary metrics
summary = analyzer.get_allocation_summary()
print(f"Capacity utilization: {summary['capacity_utilization']}%")

# Get recommendations
suggestions = analyzer.suggest_rebalancing()
for suggestion in suggestions:
    print(suggestion)


SYNTHETIC DATA GENERATOR
────────────────────────

from src.data.synthetic_data_generator import SyntheticDataGenerator

generator = SyntheticDataGenerator(seed=42)

# Generate complete dataset
dataset = generator.generate_complete_project_dataset(
    project_name="Adaptive Cruise Control",
    team_size=12,
    num_stories=30,
    num_historical_sprints=10
)

# Access components
team_df = dataset["team"]
backlog_df = dataset["backlog"]
sprints_df = dataset["historical_sprints"]
risks_df = dataset["risks"]


# ============================================================================
# TYPICAL WORKFLOW
# ============================================================================

1. GENERATE DATA
   generator = SyntheticDataGenerator(seed=42)
   dataset = generator.generate_complete_project_dataset(...)

2. ANALYZE VELOCITY
   predictor = VelocityPredictor(dataset["historical_sprints"])
   prediction = predictor.predict_velocity()
   safe_velocity = predictor.get_safe_velocity_estimate()

3. ALLOCATE RESOURCES
   analyzer = ResourceLoadAnalyzer(dataset["team"], dataset["backlog"])
   result = analyzer.allocate_resources()

4. IDENTIFY BOTTLENECKS
   suggestions = analyzer.suggest_rebalancing()

5. MAKE DECISIONS
   - Adjust scope based on safe velocity
   - Rebalance load to resolve bottlenecks
   - Negotiate for additional capacity if needed


# ============================================================================
# KEY METRICS
# ============================================================================

VELOCITY METRICS:
- Point Estimate: Expected velocity (SP)
- Lower Bound: Conservative estimate (80% confidence)
- Upper Bound: Optimistic estimate (80% confidence)
- Volatility: Standard deviation of velocity
- Trend: Historical improvement/decline
- Risk Level: Low/Medium/High based on stability

RESOURCE METRICS:
- Assignment Rate: % of tasks allocated (%)
- Feasibility: Can team handle allocated work? (Y/N)
- Capacity Utilization: % of available hours used (%)
- Load Status per member: Available/Warning/At Capacity/Overloaded
- Bottlenecks: Skill gaps, overloaded members, critical resources


# ============================================================================
# CUSTOMIZATION
# ============================================================================

CHANGE TEAM COMPOSITION:
- Modify team_size parameter in generator
- Adjust role distribution in SyntheticDataGenerator.ROLE_SKILLS

CHANGE BACKLOG COMPLEXITY:
- Modify num_stories parameter
- Adjust ASIL distribution in generate_product_backlog()
- Change task dependencies logic

ADJUST FORECAST PARAMETERS:
- Change lookback_sprints for predictor (default: 3)
- Modify confidence_level (default: 0.80)
- Adjust risk_tolerance for safe velocity

CUSTOMIZE ALLOCATION HEURISTIC:
- Modify priority scoring in Task.get_priority_score()
- Change allocation strategy in allocate_resources()
- Adjust bottleneck thresholds


# ============================================================================
# TROUBLESHOOTING
# ============================================================================

ISSUE: "ModuleNotFoundError: No module named 'streamlit'"
SOLUTION: pip install streamlit

ISSUE: "ModuleNotFoundError: No module named 'src'"
SOLUTION: Ensure you're running from automotive-dss directory
          The app.py file adds src to path automatically

ISSUE: Plots not showing in Streamlit
SOLUTION: Plots are shown via st.pyplot(fig) - this is correct

ISSUE: Synthetic data looks unrealistic
SOLUTION: Adjust distributions in SyntheticDataGenerator
          Increase historical sprints for better velocity trends
          Modify ASIL_EFFORT_MULTIPLIERS


# ============================================================================
# NEXT STEPS
# ============================================================================

1. ✓ Review this quick start guide
2. Run: streamlit run app.py
3. Explore the 3-tab dashboard interface
4. Generate different datasets with custom parameters
5. Experiment with different team sizes and workloads
6. Review the research report for theoretical background
7. Customize modules for your specific automotive context
8. Integrate with real project data when available


QUESTIONS? SEE README.md FOR DETAILED DOCUMENTATION
"""
