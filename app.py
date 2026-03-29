"""
Automotive Decision Support System (DSS) - Main Application
Streamlit-based interactive dashboard for sprint planning and resource analysis.
Integrates Velocity Predictor and Resource Load Analyzer modules.
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.data.synthetic_data_generator import SyntheticDataGenerator
from src.modules.velocity_predictor import VelocityPredictor
from src.modules.resource_load_analyzer import ResourceLoadAnalyzer


# Page configuration
st.set_page_config(
    page_title="Automotive DSS - Sprint Planning",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM PROFESSIONAL STYLING
# ============================================================================

st.markdown("""
<style>
    /* Main container styling */
    .main {
        background-color: #fafafa;
        padding: 20px;
    }
    
    /* Typography */
    .main-header {
        color: #0d47a1;
        font-size: 2.8em;
        font-weight: 700;
        margin-bottom: 10px;
        letter-spacing: -0.5px;
    }
    
    .main-subtitle {
        color: #455a64;
        font-size: 1.1em;
        font-weight: 500;
        margin-bottom: 20px;
    }
    
    /* Section headers */
    .section-header {
        color: #1565c0;
        font-size: 1.8em;
        font-weight: 700;
        margin-top: 25px;
        margin-bottom: 15px;
        border-bottom: 3px solid #1976d2;
        padding-bottom: 10px;
    }
    
    /* Subsection headers */
    .subsection-header {
        color: #0d47a1;
        font-size: 1.3em;
        font-weight: 600;
        margin: 15px 0 10px 0;
        padding-left: 10px;
        border-left: 4px solid #1976d2;
    }
    
    /* Metric cards */
    .metric-card {
        padding: 20px;
        border-radius: 8px;
        background: linear-gradient(135deg, #f5f7fa 0%, #fafafa 100%);
        border: 1px solid #e0e0e0;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .metric-value {
        font-size: 2em;
        font-weight: 700;
        color: #0d47a1;
    }
    
    .metric-label {
        font-size: 0.95em;
        color: #616161;
        font-weight: 500;
        margin-top: 5px;
    }
    
    /* Status badges */
    .badge-success {
        background-color: #e8f5e9;
        color: #2e7d32;
        padding: 8px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85em;
        border: 1px solid #81c784;
    }
    
    .badge-warning {
        background-color: #fff3e0;
        color: #e65100;
        padding: 8px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85em;
        border: 1px solid #ffb74d;
    }
    
    .badge-danger {
        background-color: #ffebee;
        color: #c62828;
        padding: 8px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85em;
        border: 1px solid #ef5350;
    }
    
    .badge-info {
        background-color: #e3f2fd;
        color: #1565c0;
        padding: 8px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85em;
        border: 1px solid #64b5f6;
    }
    
    /* Text colors */
    .success {
        color: #2e7d32;
        font-weight: 600;
    }
    
    .warning {
        color: #e65100;
        font-weight: 600;
    }
    
    .danger {
        color: #c62828;
        font-weight: 600;
    }
    
    .info {
        color: #1565c0;
        font-weight: 600;
    }
    
    /* Dividers */
    hr {
        border: none;
        border-top: 2px solid #e0e0e0;
        margin: 25px 0;
    }
    
    /* Info boxes */
    .info-box {
        background-color: #e3f2fd;
        border-left: 4px solid #1976d2;
        padding: 15px 20px;
        border-radius: 4px;
        margin: 15px 0;
    }
    
    .success-box {
        background-color: #e8f5e9;
        border-left: 4px solid #4caf50;
        padding: 15px 20px;
        border-radius: 4px;
        margin: 15px 0;
    }
    
    .warning-box {
        background-color: #fff3e0;
        border-left: 4px solid #ff9800;
        padding: 15px 20px;
        border-radius: 4px;
        margin: 15px 0;
    }
    
    .error-box {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
        padding: 15px 20px;
        border-radius: 4px;
        margin: 15px 0;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #757575;
        font-size: 0.85em;
        margin-top: 40px;
        padding-top: 20px;
        border-top: 2px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# INITIALIZATION & CACHING
# ============================================================================

@st.cache_resource
def initialize_generator():
    """Initialize synthetic data generator"""
    return SyntheticDataGenerator(seed=42)


@st.cache_data
def load_dataset(project_name, team_size, num_stories, num_sprints):
    """Load/generate dataset"""
    generator = initialize_generator()
    return generator.generate_complete_project_dataset(
        project_name=project_name,
        team_size=team_size,
        num_stories=num_stories,
        num_historical_sprints=num_sprints
    )


# ============================================================================
# SIDEBAR CONFIGURATION
# ============================================================================

st.sidebar.markdown("# ⚙️ Configuration")

# Project parameters
st.sidebar.subheader("Project Setup")
project_name = st.sidebar.text_input(
    "Project Name",
    value="Adaptive Cruise Control (ACC)",
    help="Name of the automotive feature being developed"
)

team_size = st.sidebar.slider(
    "Team Size",
    min_value=5,
    max_value=20,
    value=12,
    help="Number of team members"
)

num_stories = st.sidebar.slider(
    "Backlog Size",
    min_value=15,
    max_value=50,
    value=30,
    help="Number of user stories to generate"
)

num_sprints = st.sidebar.slider(
    "Historical Sprints",
    min_value=5,
    max_value=20,
    value=10,
    help="Number of past sprints for velocity analysis"
)

# Load data
if st.sidebar.button("🔄 Generate Dataset"):
    st.session_state.clear()
    st.cache_data.clear()
    st.rerun()

dataset = load_dataset(project_name, team_size, num_stories, num_sprints)

# Store in session state
if "dataset" not in st.session_state:
    st.session_state.dataset = dataset

st.sidebar.success("✓ Dataset loaded")

# ============================================================================
# MAIN CONTENT
# ============================================================================

# ============================================================================
# MAIN APPLICATION HEADER
# ============================================================================

# Professional header
st.markdown(f'<p class="main-header">🚗 Automotive Decision Support System</p>', unsafe_allow_html=True)
st.markdown(f'<p class="main-subtitle">Intelligent Sprint Planning & Resource Optimization Platform</p>', unsafe_allow_html=True)

# Project info badges
col_info1, col_info2, col_info3, col_info4 = st.columns(4)
with col_info1:
    st.metric("📋 Project", project_name)
with col_info2:
    st.metric("👥 Team Size", f"{team_size} Members")
with col_info3:
    st.metric("📚 Backlog", f"{num_stories} Stories")
with col_info4:
    st.metric("📈 History", f"{num_sprints} Sprints")

st.divider()

# Create tabs
tab1, tab2, tab3 = st.tabs(
    ["📊 Velocity Forecasting", "👥 Resource Analysis", "📋 Data Explorer"]
)

# ============================================================================
# TAB 1: VELOCITY FORECASTING
# ============================================================================

# ============================================================================
# TAB 1: VELOCITY FORECASTING
# ============================================================================

with tab1:
    st.markdown('<p class="section-header">📊 Sprint Velocity Forecasting</p>', unsafe_allow_html=True)
    st.markdown("**Plan your next sprint with confidence!** This tool provides data-driven velocity predictions based on historical team performance and Monte Carlo simulation.")

    # Quick explanation
    with st.expander("📖 How does velocity forecasting work?", expanded=False):
        st.markdown("""
        ##### Understanding Velocity Forecasting
        
        **The Core Question:** *"How many story points can our team reliably commit to next sprint?"*
        
        **Our Approach:**
        - 📈 **Historical Analysis**: Analyzes your last few sprints to identify velocity patterns
        - 📉 **Trend Detection**: Detects if your team is accelerating, decelerating, or maintaining pace
        - 🎲 **Monte Carlo Simulation**: Runs 10,000+ scenarios to account for variability
        - 📊 **Confidence Intervals**: Provides safe, realistic, and optimistic estimates
        - 🎯 **Risk Assessment**: Calculates probability of achieving target story points
        
        **Why This Matters:**
        - ✓ Reduces missed commitments and team frustration
        - ✓ Improves stakeholder confidence and predictability
        - ✓ Enables better capacity planning for safety-critical work
        - ✓ Supports compliance with automotive standards
        
        **The Process:**
        1. **Historical Analysis**: Looks at your last few sprints to understand patterns
        2. **Trend Detection**: Identifies if your team is getting faster or slower
        3. **Risk Assessment**: Calculates uncertainty using statistical methods
        4. **Monte Carlo Simulation**: Runs thousands of "what-if" scenarios

        **Why it matters:** Better planning = fewer missed deadlines and happier teams!
        """)

    col1, col2 = st.columns([1, 1])

    with col1:
        # Initialize predictor
        predictor = VelocityPredictor(
            st.session_state.dataset["historical_sprints"],
            lookback_sprints=3
        )

        # Get prediction
        prediction = predictor.predict_velocity(confidence_level=0.80)

        st.subheader("📊 Key Metrics")

        # Main prediction in a prominent box
        st.info(f"""
        **🎯 Next Sprint Forecast (80% confidence):**
        - **Most likely:** {prediction['point_estimate']} story points
        - **Safe range:** {prediction['lower_bound']:.0f} - {prediction['upper_bound']:.0f} story points
        - **Don't plan for more than:** {prediction['upper_bound']:.0f} points (too risky!)
        """)

        metric_cols = st.columns(2)
        with metric_cols[0]:
            st.metric(
                "Recent Performance",
                f"{predictor.baseline_velocity:.1f} SP avg",
                f"Trend: {prediction['trend']:+.2f} SP/sprint",
                help="Average of last 3 sprints. Positive trend = team improving!"
            )

            st.metric(
                "Risk Level",
                f"{prediction['volatility']:.1f} SP variation",
                help="How much your velocity typically varies. Lower = more predictable."
            )

        with metric_cols[1]:
            # Team health status
            health = predictor.analyze_sprint_health()
            stability = health.get("stability", "Unknown")
            risk_level = health.get("risk_level", "Unknown")

            # Color-code the health status
            if risk_level == "Low":
                health_color = "🟢"
                health_desc = "Stable & Predictable"
            elif risk_level == "Medium":
                health_color = "🟡"
                health_desc = "Some Variation"
            else:
                health_color = "🔴"
                health_desc = "High Risk"

            st.metric(
                "Team Health",
                f"{health_color} {health_desc}",
                f"Stability: {stability}"
            )

            # Safe velocity recommendation
            safe_velocity = predictor.get_safe_velocity_estimate(0.20)
            st.metric(
                "Safe Commitment",
                f"{safe_velocity} SP",
                help="Maximum points with 80% success chance"
            )

    with col2:
        st.subheader("💡 Planning Insights")

        # Sprint planning recommendations
        st.markdown("### Sprint Planning Guide")

        if prediction['point_estimate'] < 20:
            st.warning("⚠️ **Small Team Alert:** Your velocity suggests a small team. Consider these planning tips:")
            st.markdown("- Focus on high-value features first")
            st.markdown("- Keep sprint goals realistic (15-25 points)")
            st.markdown("- Consider adding team members if possible")
        elif prediction['volatility'] > predictor.baseline_velocity * 0.3:
            st.warning("⚠️ **High Variation Alert:** Your team's velocity varies significantly:")
            st.markdown("- Plan for uncertainty - use lower end of range")
            st.markdown("- Keep some buffer for unexpected issues")
            st.markdown("- Focus on improving estimation accuracy")
        else:
            st.success("✅ **Good Planning Position:** Your team shows consistent performance:")
            st.markdown("- Use the full forecast range for planning")
            st.markdown("- Consider stretch goals within safe limits")
            st.markdown("- Good foundation for capacity planning")

        # Quick probability calculator
        st.markdown("### Quick Probability Check")
        test_points = st.slider(
            "Test different story point targets:",
            min_value=int(prediction['lower_bound']),
            max_value=int(prediction['upper_bound'] + 10),
            value=int(prediction['point_estimate']),
            help="See success probability for different sprint goals"
        )

        prob_success = predictor.estimate_sprint_completion_probability(test_points, 0.80)
        prob_color = "🟢" if prob_success > 0.8 else "🟡" if prob_success > 0.6 else "🔴"

        st.metric(
            f"Success Chance for {test_points} SP",
            f"{prob_color} {prob_success:.1%}",
            help="Probability of completing at least this many points"
        )

    st.divider()

    # Velocity forecast report
    st.subheader("🎯 Sprint Planning Scenarios")

    st.markdown("**Choose your sprint goal:** Compare different story point targets with success probabilities.")

    report = predictor.generate_velocity_report(
        planned_sp_options=[20, 25, 30, 35, 40, 45, 50]
    )

    # Enhanced risk highlighting
    def highlight_risk_enhanced(row):
        if row["SuccessProbability"] > 80:
            return ["background-color: #E8F5E9; color: #2E7D32"] * len(row)  # Green
        elif row["SuccessProbability"] > 60:
            return ["background-color: #FFF3E0; color: #E65100"] * len(row)  # Orange
        else:
            return ["background-color: #FFEBEE; color: #C62828"] * len(row)  # Red

    st.dataframe(
        report.style.apply(highlight_risk_enhanced, axis=1),
        width='stretch',
        hide_index=True,
        column_config={
            "PlannedSP": st.column_config.NumberColumn("Sprint Goal", help="Story points to plan for"),
            "SuccessProbability": st.column_config.NumberColumn("Success Chance", help="Probability of completing this many points", format="%.1f%%"),
            "RiskCategory": st.column_config.TextColumn("Risk Level", help="Low/Medium/High risk assessment"),
            "Recommendation": st.column_config.TextColumn("Planning Advice", help="Recommendation for this target")
        }
    )

    st.markdown("""
    **💡 Reading the table:**
    - 🟢 **Green rows:** Safe bets (80%+ success chance)
    - 🟠 **Orange rows:** Possible but risky (60-80% chance)
    - 🔴 **Red rows:** High risk (below 60% chance)
    """)

    st.divider()

    # Visualizations with better explanations
    st.subheader("📈 Understanding Your Team's Performance")

    col_a, col_b = st.columns([1, 1])

    with col_a:
        st.markdown("### Past Performance & Next Sprint Forecast")
        st.markdown("*This chart shows your team's actual velocity history and predicts the next sprint.*")

        fig = predictor.plot_velocity_forecast(figsize=(10, 5))
        st.pyplot(fig)

        st.markdown("""
        **📊 How to read this chart:**
        - **Blue dots:** Your actual performance in past sprints
        - **Purple line:** Overall trend (up = improving, down = challenges)
        - **Green line:** Recent average performance
        - **Orange box:** Next sprint prediction range (80% confidence)
        - **Red star:** Most likely outcome
        """)

    with col_b:
        st.markdown("### What Are Our Chances Next Sprint?")
        st.markdown("*This shows the probability distribution of what your team might achieve.*")

        fig = predictor.plot_probability_distribution(figsize=(10, 5))
        st.pyplot(fig)

        st.markdown("""
        **🎲 Understanding probabilities:**
        - **Green line (50%):** Coin flip - might complete, might not
        - **Orange line (80%):** Good bet - likely to succeed
        - **Red line (90%):** Optimistic - best case scenario
        - **Purple line:** Your recent average performance
        """)

    # Additional insights
    st.subheader("🔍 Key Insights & Recommendations")

    insights_cols = st.columns(2)

    with insights_cols[0]:
        st.markdown("### Capacity Planning")
        if prediction['trend'] > 0:
            st.success(f"📈 **Improving Trend:** Team velocity is increasing by {prediction['trend']:.1f} SP per sprint. Consider larger goals in future sprints.")
        elif prediction['trend'] < -1:
            st.warning(f"📉 **Declining Trend:** Team velocity is decreasing. Investigate blockers or consider smaller sprint goals.")
        else:
            st.info(f"➡️ **Stable Performance:** Consistent velocity around {predictor.baseline_velocity:.1f} SP. Good foundation for planning.")

        st.markdown(f"**Recommended Sprint Range:** {prediction['lower_bound']:.0f} - {prediction['upper_bound']:.0f} story points")

    with insights_cols[1]:
        st.markdown("### Risk Management")
        cv = health.get('coefficient_of_variation', 0)
        if cv < 0.2:
            st.success("🛡️ **Low Risk:** Very predictable performance. Can plan with confidence.")
        elif cv < 0.4:
            st.info("⚠️ **Medium Risk:** Some variation expected. Plan conservatively.")
        else:
            st.warning("🚨 **High Risk:** Significant uncertainty. Use lower planning targets.")

        st.markdown(f"**Safe Planning Target:** {safe_velocity} story points (80% success chance)")

    st.divider()

    # Safety-Critical Delivery Analysis
    st.subheader("🚗 Safety-Critical Delivery Impact (ASIL-C/D Tasks)")
    
    safety_impact = predictor.analyze_safety_impact(total_safety_critical_points=50)
    
    col_safety1, col_safety2 = st.columns([1.5, 1])
    
    with col_safety1:
        # Display status with appropriate color
        if "SAFE" in safety_impact["status"]:
            st.success(f"### {safety_impact['status']}")
        elif "CAUTION" in safety_impact["status"]:
            st.warning(f"### {safety_impact['status']}")
        else:
            st.error(f"### {safety_impact['status']}")
        
        st.markdown("**Impact on Safety-Critical Milestones:**")
        st.markdown(f"- **Total ASIL-C/D Points:** {safety_impact['total_safety_points']} SP")
        st.markdown(f"- **Completion Probability (5-sprint target):** `{safety_impact['completion_probability']:.1f}%`")
        st.markdown(f"- **Sprints Needed (80% confidence):** `{safety_impact['sprints_needed_80_confidence']:.1f}`")
        st.markdown(f"- **Sprints Needed (Safe estimate):** `{safety_impact['sprints_needed_safe']:.1f}`")
        st.markdown(f"\n**Recommendation:** {safety_impact['recommendation']}")
    
    with col_safety2:
        st.markdown("### Key Considerations")
        st.markdown("""
        **ASIL Levels & Impact:**
        - 🔴 **ASIL-D:** Highest criticality
        - 🟠 **ASIL-C:** High criticality
        - 🟡 **ASIL-B:** Medium criticality
        - 🟢 **ASIL-A:** Low criticality
        - ⚪ **QM:** No safety requirement
        
        **Plan buffer capacity for safety-critical work to minimize deadline risk.**
        """)

# ============================================================================
# TAB 2: RESOURCE ANALYSIS
# ============================================================================

with tab2:
    st.markdown('<p class="section-header">👥 Resource Load Analysis</p>', unsafe_allow_html=True)
    st.markdown("**Optimize team capacity and identify bottlenecks.** Allocate tasks efficiently while maintaining awareness of safety-critical work (ASIL-C/D tasks).")
    
    # Initialize analyzer
    analyzer = ResourceLoadAnalyzer(
        st.session_state.dataset["team"],
        st.session_state.dataset["backlog"]
    )
    
    # Perform allocation with strict capacity and skill constraints
    allocation_result = analyzer.allocate_resources(respect_capacity_limits=True)
    summary = analyzer.get_allocation_summary()
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Assignment Rate",
            f"{summary['assignment_rate']}%",
            delta=f"{summary['assigned_tasks']}/{summary['total_tasks']}"
        )
    
    with col2:
        utilization_color = "🟢" if summary['capacity_utilization'] < 85 else (
            "🟡" if summary['capacity_utilization'] < 100 else "🔴"
        )
        st.metric(
            "Capacity Utilization",
            f"{utilization_color} {summary['capacity_utilization']}%"
        )
    
    with col3:
        st.metric(
            "Total Load",
            f"{summary['total_load']:.0f}h",
            delta=f"/ {summary['total_team_capacity']}h"
        )
    
    with col4:
        team_count = len(analyzer.team)
        st.metric(
            "Team Size",
            f"{team_count} members",
            delta=f"Avg {summary['total_load'] / max(1, team_count):.1f}h per person"
        )
    
    st.divider()
    
    # Safety-Critical Analysis Section
    st.subheader("🚨 Safety-Criticality (ASIL) Analysis")
    
    safety_alerts = analyzer.get_safety_critical_bottlenecks()
    if safety_alerts:
        st.warning("**Critical Safety Concerns Detected:**")
        for alert in safety_alerts:
            if alert.startswith("🚨"):
                st.error(alert)
            elif alert.startswith("⚠️"):
                st.warning(alert)
            else:
                st.info(alert)
    else:
        st.success("✓ No critical safety bottlenecks detected")
    
    # ASIL Distribution Chart
    col_asil1, col_asil2 = st.columns([1.2, 1])
    
    with col_asil1:
        fig = analyzer.generate_asil_distribution_chart(figsize=(10, 5))
        st.pyplot(fig)
    
    with col_asil2:
        st.markdown("### ASIL Distribution Summary")
        asil_dist = analyzer.get_asil_distribution()
        
        asil_colors = {
            "D": "🔴", "C": "🟠", "B": "🟡", "A": "🟢", "QM": "⚪"
        }
        asil_names = {
            "D": "Highest Critical",
            "C": "High Critical",
            "B": "Medium Critical",
            "A": "Low Critical",
            "QM": "No Safety Req."
        }
        
        for asil in ["D", "C", "B", "A", "QM"]:
            if asil in asil_dist:
                info = asil_dist[asil]
                st.metric(
                    f"{asil_colors[asil]} ASIL-{asil}: {asil_names[asil]}",
                    f"{info['count']} tasks",
                    f"{info['hours']:.0f}h ({info['percentage']:.1f}%)"
                )
    
    st.divider()
    
    # Infeasible tasks breakdown
    if allocation_result["infeasible_tasks"]:
        st.subheader("❌ Unmet Constraints (Infeasible Tasks)")
        infeasible_breakdown = {}
        for task in allocation_result["infeasible_tasks"]:
            reason = task.bottleneck_reason or "Unknown"
            infeasible_breakdown[reason] = infeasible_breakdown.get(reason, 0) + 1
        
        col_infeasible1, col_infeasible2 = st.columns(2)
        with col_infeasible1:
            st.error(f"**Total unassigned/constrained: {len(allocation_result['infeasible_tasks'])} tasks**")
            for reason, count in infeasible_breakdown.items():
                st.write(f"- {reason}: {count} task(s)")
        
        with col_infeasible2:
            st.warning("**Recommended Actions:**")
            for reason, count in infeasible_breakdown.items():
                if "Insufficient capacity" in reason:
                    st.write(f"- Add {count * 5}-{count * 10}h team capacity or defer {count} task(s)")
                elif "No team member with required skills" in reason:
                    st.write(f"- Hire specialist or train member for required skills ({count} task(s) affected)")
                else:
                    st.write(f"- Review constraints for {reason} ({count} task(s))")
        st.divider()
    
    # Team status table
    st.subheader("Team Member Workload")
    team_status = analyzer._get_team_status()
    
    # Add recommended actions column
    def get_action(row):
        if row["Status"] == "Overloaded":
            return f"Reassign {abs(row['Remaining']):.0f}h of tasks"
        elif row["Status"] == "At Capacity":
            return "Monitor closely - at limit"
        elif row["Status"] == "Warning":
            return f"Can take {row['Remaining']:.0f}h more"
        else:
            return f"Available for {row['Remaining']:.0f}h"
    
    team_status["Recommended Action"] = team_status.apply(get_action, axis=1)
    
    # Color code by status
    def color_status(val):
        if val == "Overloaded":
            return "color: #D32F2F; font-weight: bold"
        elif val == "At Capacity":
            return "color: #F57C00; font-weight: bold"
        elif val == "Warning":
            return "color: #FBC02D; font-weight: bold"
        else:
            return "color: #388E3C; font-weight: bold"
    
    styled_team = team_status.style.map(
        color_status,
        subset=["Status"]
    )
    
    st.dataframe(styled_team, width='stretch', hide_index=True)
    
    st.divider()
    
    # Visualizations
    col_viz1, col_viz2 = st.columns([1, 1])
    
    with col_viz1:
        st.subheader("Resource Load Heatmap")
        fig = analyzer.generate_load_heatmap(figsize=(12, 6))
        st.pyplot(fig)
    
    with col_viz2:
        st.subheader("Skill Coverage")
        fig = analyzer.generate_skill_coverage_chart(figsize=(12, 6))
        st.pyplot(fig)
    
    st.divider()
    
    # Bottleneck analysis and recommendations
    st.subheader("⚠️ Bottleneck Analysis & Recommendations")
    
    suggestions = analyzer.suggest_rebalancing()
    
    for suggestion in suggestions:
        if suggestion.startswith("✓"):
            st.success(suggestion)
        elif suggestion.startswith("✗"):
            st.error(suggestion)
        elif suggestion.startswith("⚠"):
            st.warning(suggestion)
        else:
            st.info(suggestion)
    
    # Task allocation details
    st.subheader("Task Allocation Details")
    allocation_df = allocation_result["allocation_df"].copy()
    
    # Add color coding based on comprehensive status types
    def style_task_status(val):
        status_colors = {
            "Assigned": "background-color: #C8E6C9; color: #2E7D32; font-weight: bold",      # Green
            "Overloaded": "background-color: #FFE0B2; color: #E65100; font-weight: bold",    # Orange
            "Delayed": "background-color: #FFF9C4; color: #F57F17; font-weight: bold",       # Yellow
            "Unassigned": "background-color: #FFCDD2; color: #C62828; font-weight: bold",    # Red
            "Cancelled": "background-color: #EEEEEE; color: #616161; font-weight: bold",     # Gray
        }
        return status_colors.get(str(val), "background-color: #FFFFFF")
    
    styled_allocation = allocation_df.style.map(
        style_task_status,
        subset=["Status"]
    )
    
    st.dataframe(
        styled_allocation,
        width='stretch',
        hide_index=True
    )
    
    # Summary of task statuses
    st.subheader("Status Breakdown")
    status_counts = allocation_df["Status"].value_counts()
    
    col_status1, col_status2, col_status3, col_status4 = st.columns(4)
    
    with col_status1:
        assigned_count = status_counts.get("Assigned", 0)
        st.metric("✓ Assigned", int(assigned_count), delta="Within capacity")
    
    with col_status2:
        overloaded_count = status_counts.get("Overloaded", 0)
        if overloaded_count > 0:
            st.warning(f"⚠️ Overloaded: **{int(overloaded_count)}**")
        else:
            st.metric("⚠️ Overloaded", int(overloaded_count), delta="None")
    
    with col_status3:
        unassigned_count = status_counts.get("Unassigned", 0)
        if unassigned_count > 0:
            st.error(f"✗ Unassigned: **{int(unassigned_count)}**")
        else:
            st.metric("✗ Unassigned", int(unassigned_count), delta="None")
    
    with col_status4:
        cancelled_count = status_counts.get("Cancelled", 0)
        if cancelled_count > 0:
            st.error(f"❌ Cancelled: **{int(cancelled_count)}** (Skill gaps)")
        else:
            st.metric("❌ Cancelled", int(cancelled_count), delta="None")
    
    # Detailed recommendations by status
    st.divider()
    st.subheader("Status Recommendations")
    
    recommendations = {
        "Assigned": "✅ Tasks assigned within team capacity - On track",
        "Overloaded": "⚠️ Tasks assigned but team member exceeded capacity - Review workload or add resources",
        "Delayed": "⏳ Tasks waiting for dependencies or constraints to be resolved",
        "Unassigned": "❌ Tasks could not be assigned due to capacity/skill constraints - Requires action",
        "Cancelled": "🚫 Tasks cancelled due to missing required skills - Consider hiring or training",
    }
    
    for status, recommendation in recommendations.items():
        count = status_counts.get(status, 0)
        if count > 0:
            if "✅" in recommendation:
                st.success(f"{recommendation} ({int(count)} tasks)")
            elif "⚠️" in recommendation:
                st.warning(f"{recommendation} ({int(count)} tasks)")
            elif "❌" in recommendation or "🚫" in recommendation:
                st.error(f"{recommendation} ({int(count)} tasks)")
            else:
                st.info(f"{recommendation} ({int(count)} tasks)")

# ============================================================================
# TAB 3: DATA EXPLORER
# ============================================================================

with tab3:
    st.header("📋 Dataset Explorer")
    st.markdown("Examine the synthetic project data in detail.")
    
    data_tabs = st.tabs([
        "Team Members",
        "Product Backlog",
        "Historical Sprints",
        "Risk Register"
    ])
    
    with data_tabs[0]:
        st.subheader("Team Members")
        st.dataframe(
            st.session_state.dataset["team"],
            width='stretch',
            hide_index=True
        )
        
        st.download_button(
            "📥 Download Team CSV",
            st.session_state.dataset["team"].to_csv(index=False),
            "team_members.csv",
            "text/csv"
        )
    
    with data_tabs[1]:
        st.subheader("Product Backlog")
        st.dataframe(
            st.session_state.dataset["backlog"],
            width='stretch',
            hide_index=True
        )
        
        st.download_button(
            "📥 Download Backlog CSV",
            st.session_state.dataset["backlog"].to_csv(index=False),
            "product_backlog.csv",
            "text/csv"
        )
    
    with data_tabs[2]:
        st.subheader("Historical Sprint Data")
        st.dataframe(
            st.session_state.dataset["historical_sprints"],
            width='stretch',
            hide_index=True
        )
        
        st.download_button(
            "📥 Download Sprints CSV",
            st.session_state.dataset["historical_sprints"].to_csv(index=False),
            "historical_sprints.csv",
            "text/csv"
        )
    
    with data_tabs[3]:
        st.subheader("Risk Register")
        st.dataframe(
            st.session_state.dataset["risks"],
            use_container_width=True,
            hide_index=True
        )
        
        st.download_button(
            "📥 Download Risks CSV",
            st.session_state.dataset["risks"].to_csv(index=False),
            "risk_register.csv",
            "text/csv"
        )

# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.markdown("""---
**Automotive Decision Support System (DSS) v1.0**

Built with synthetic data generation, stochastic velocity forecasting, and heuristic resource allocation.

*For automotive Agile project management with safety-critical constraints (ISO 26262, ASPICE)*
""")
