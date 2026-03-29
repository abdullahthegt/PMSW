"""
Example usage script for Automotive DSS
Demonstrates core functionality without Streamlit
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from data.synthetic_data_generator import SyntheticDataGenerator
from modules.velocity_predictor import VelocityPredictor
from modules.resource_load_analyzer import ResourceLoadAnalyzer


def print_section(title):
    """Print formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def main():
    """Run example analysis"""
    
    print_section("AUTOMOTIVE DECISION SUPPORT SYSTEM - EXAMPLE")
    
    # ========================================================================
    # STEP 1: GENERATE SYNTHETIC DATA
    # ========================================================================
    
    print_section("Step 1: Generate Synthetic Project Data")
    
    generator = SyntheticDataGenerator(seed=42)
    
    print("Generating synthetic dataset...")
    dataset = generator.generate_complete_project_dataset(
        project_name="Adaptive Cruise Control (ACC)",
        team_size=12,
        num_stories=30,
        num_historical_sprints=10
    )
    
    print(f"\n✓ Dataset generated successfully")
    print(f"  • Team members: {len(dataset['team'])}")
    print(f"  • Backlog items: {len(dataset['backlog'])}")
    print(f"  • Historical sprints: {len(dataset['historical_sprints'])}")
    print(f"  • Risk items: {len(dataset['risks'])}")
    
    # ========================================================================
    # STEP 2: VELOCITY FORECASTING
    # ========================================================================
    
    print_section("Step 2: Sprint Velocity Analysis")
    
    predictor = VelocityPredictor(
        dataset["historical_sprints"],
        lookback_sprints=3
    )
    
    # Get prediction
    prediction = predictor.predict_velocity(confidence_level=0.80)
    
    print("\n📊 Velocity Forecast (80% Confidence):")
    print(f"  • Point Estimate:        {prediction['point_estimate']} SP")
    print(f"  • Lower Bound:           {prediction['lower_bound']} SP")
    print(f"  • Upper Bound:           {prediction['upper_bound']} SP")
    print(f"  • Volatility (σ):        {prediction['volatility']} SP")
    print(f"  • Trend:                 {prediction['trend']:+.3f}")
    print(f"  • Margin of Error:       ±{prediction['margin_of_error']} SP")
    
    # Analyze team health
    health = predictor.analyze_sprint_health()
    
    print("\n🏥 Team Health Assessment:")
    print(f"  • Baseline Velocity:     {health['baseline_velocity']} SP")
    print(f"  • Stability:             {health['stability']}")
    print(f"  • Trend:                 {health['trend']}")
    print(f"  • Risk Level:            {health['risk_level']}")
    print(f"  • Coefficient of Variation: {health['coefficient_of_variation']:.3f}")
    
    # Planning options
    print("\n📋 Planning Options Analysis:")
    report = predictor.generate_velocity_report(planned_sp_options=[30, 35, 40, 45, 50])
    
    for _, row in report.iterrows():
        status = "✓" if "Safe" in row["Recommendation"] else "⚠" if "Caution" in row["Recommendation"] else "✗"
        print(f"  {status} {row['PlannedSP']} SP: {row['SuccessProbability']:.1f}% success - {row['RiskCategory']}")
    
    # Safe velocity
    safe_velocity = predictor.get_safe_velocity_estimate(risk_tolerance=0.20)
    print(f"\n💡 Recommended 'Safe' Velocity: {safe_velocity} SP (80% success probability)")
    
    # ========================================================================
    # STEP 3: RESOURCE ALLOCATION ANALYSIS
    # ========================================================================
    
    print_section("Step 3: Resource Allocation & Bottleneck Analysis")
    
    analyzer = ResourceLoadAnalyzer(
        dataset["team"],
        dataset["backlog"]
    )
    
    print("\nPerforming resource allocation...")
    result = analyzer.allocate_resources()
    summary = analyzer.get_allocation_summary()
    
    print("\n📊 Allocation Summary:")
    print(f"  • Total Tasks:           {summary['total_tasks']}")
    print(f"  • Assigned Tasks:        {summary['assigned_tasks']} ({summary['assignment_rate']:.1f}%)")
    print(f"  • Feasible Tasks:        {summary['feasible_tasks']} ({summary['feasibility_rate']:.1f}%)")
    print(f"  • Team Capacity:         {summary['total_team_capacity']} hours")
    print(f"  • Total Load:            {summary['total_load']:.0f} hours")
    print(f"  • Utilization:           {summary['capacity_utilization']:.1f}%")
    print(f"  • Status:                {'✓ FEASIBLE' if summary['is_feasible'] else '✗ INFEASIBLE'}")
    
    # Team status
    print("\n👥 Team Member Load Status:")
    team_status = analyzer._get_team_status()
    for _, member in team_status.head(5).iterrows():
        status_icon = "🟢" if member["Status"] == "Available" else "🟡" if member["Status"] == "Warning" else "🔴"
        print(f"  {status_icon} {member['Name']:20s} | {member['Role']:15s} | "
              f"Load: {member['LoadPercent']:5.1f}% | Status: {member['Status']}")
    
    if len(team_status) > 5:
        print(f"  ... and {len(team_status) - 5} more members")
    
    # Bottleneck analysis
    print("\n⚠️ Bottleneck Analysis:")
    
    bottlenecks = result["bottleneck_analysis"]
    
    if bottlenecks["overloaded_members"]:
        print("  🔴 OVERLOADED MEMBERS:")
        for overload in bottlenecks["overloaded_members"]:
            print(f"      • {overload['name']}: +{overload['overload_hours']:.1f} hours over capacity")
    
    if bottlenecks["skill_gaps"]:
        print("  🟡 SKILL GAPS:")
        for skill, count in bottlenecks["skill_gaps"].items():
            if count == 0:
                print(f"      • '{skill}': NO COVERAGE (Critical!)")
            elif count == 1:
                print(f"      • '{skill}': Only 1 person (Single point of failure)")
    
    if not bottlenecks["overloaded_members"] and not bottlenecks["skill_gaps"]:
        print("  ✓ No critical bottlenecks detected")
    
    # Recommendations
    print("\n💡 Rebalancing Recommendations:")
    suggestions = analyzer.suggest_rebalancing()
    for suggestion in suggestions[:5]:  # Show top 5
        if suggestion.startswith("✓"):
            print(f"  {suggestion}")
        elif suggestion.startswith("✗"):
            print(f"  {suggestion}")
        elif suggestion.startswith("⚠"):
            print(f"  {suggestion}")
        else:
            print(f"  • {suggestion}")
    
    # ========================================================================
    # STEP 4: SAMPLE DATA PREVIEW
    # ========================================================================
    
    print_section("Step 4: Sample Data Preview")
    
    print("\n📋 TEAM MEMBERS (first 3):")
    print(dataset["team"][["ID", "Name", "Role", "Skills", "Efficiency", "Availability_Hours"]].head(3).to_string())
    
    print("\n📋 PRODUCT BACKLOG (first 3):")
    print(dataset["backlog"][["TaskID", "Title", "Type", "ASIL", "StoryPoints", "EstimatedHours"]].head(3).to_string())
    
    print("\n📋 HISTORICAL SPRINTS (first 3):")
    print(dataset["historical_sprints"][["SprintID", "PlannedSP", "CompletedSP", "TeamSize", "RiskEventOccurred"]].head(3).to_string())
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    
    print_section("Summary & Insights")
    
    print("""
    ✓ Synthetic data generated with realistic automotive project constraints
    ✓ Velocity analysis shows team reliability and planning safety margins
    ✓ Resource allocation identifies skill gaps and bottlenecks
    ✓ Recommendations guide scope, resource, and risk decisions
    
    KEY TAKEAWAY:
    The DSS transforms single-point estimates into probabilistic forecasts,
    enabling informed decision-making under uncertainty.
    
    NEXT STEPS:
    1. Run: streamlit run app.py
    2. Explore interactive dashboard
    3. Generate multiple datasets
    4. Compare planning scenarios
    """)


if __name__ == "__main__":
    main()
