"""
Sprint Velocity Predictor Module
Implements probabilistic velocity forecasting using historical sprint data.
Addresses the "Flaw of Averages" through stochastic analysis.
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, Tuple, List
import matplotlib.pyplot as plt


class VelocityPredictor:
    """
    Predicts sprint velocity using:
    - Rolling averages for baseline
    - Standard deviation for volatility
    - Trend analysis (linear regression)
    - Confidence intervals using normal distribution
    """

    def __init__(self, historical_data: pd.DataFrame, lookback_sprints: int = 3):
        """
        Initialize predictor with historical sprint data.
        
        Args:
            historical_data: DataFrame with columns [SprintID, PlannedSP, CompletedSP, ...]
            lookback_sprints: Number of recent sprints to use for baseline
        """
        self.data = historical_data.copy()
        self.lookback_sprints = lookback_sprints
        self.baseline_velocity = None
        self.volatility = None
        self.trend = None
        self._calculate_metrics()

    def _calculate_metrics(self):
        """Calculate velocity baseline, volatility, and trend."""
        # Use CompletedSP as the actual velocity
        if len(self.data) == 0:
            raise ValueError("Historical data is empty")

        recent = self.data.tail(self.lookback_sprints)
        
        # Baseline: rolling average
        self.baseline_velocity = recent["CompletedSP"].mean()
        
        # Volatility: standard deviation
        self.volatility = recent["CompletedSP"].std()
        if np.isnan(self.volatility):
            self.volatility = 0
        
        # Trend: linear regression on all data
        if len(self.data) >= 2:
            x = np.arange(len(self.data))
            y = self.data["CompletedSP"].values
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            self.trend = slope  # Positive = improving, negative = declining
        else:
            self.trend = 0

    def predict_velocity(self, confidence_level: float = 0.80) -> Dict:
        """
        Predict next sprint velocity with confidence interval.
        
        Per Section 5.2: Forecast_{90%} = V̄ ± (1.645 × σ)
        
        Args:
            confidence_level: Confidence level (0.80 = 80%, 0.90 = 90%)
            
        Returns:
            Dict with point estimate, confidence interval, and risk assessment
        """
        # Adjust baseline by trend
        next_velocity_estimate = self.baseline_velocity + self.trend
        
        # Z-score for confidence level
        z_score = stats.norm.ppf((1 + confidence_level) / 2)
        
        # Confidence interval
        margin_of_error = z_score * self.volatility
        lower_bound = next_velocity_estimate - margin_of_error
        upper_bound = next_velocity_estimate + margin_of_error
        
        # Ensure non-negative
        lower_bound = max(0, lower_bound)
        upper_bound = max(lower_bound, upper_bound)
        
        return {
            "point_estimate": round(next_velocity_estimate, 1),
            "lower_bound": round(lower_bound, 1),
            "upper_bound": round(upper_bound, 1),
            "volatility": round(self.volatility, 2),
            "trend": round(self.trend, 3),
            "confidence_level": confidence_level,
            "margin_of_error": round(margin_of_error, 1),
        }

    def get_forecast_distribution(self, num_samples: int = 1000) -> np.ndarray:
        """
        Generate Monte Carlo samples of next sprint velocity.
        
        Args:
            num_samples: Number of samples to generate
            
        Returns:
            Array of simulated velocity values
        """
        next_mean = self.baseline_velocity + self.trend
        # Sample from normal distribution
        samples = np.random.normal(next_mean, max(1, self.volatility), num_samples)
        return np.clip(samples, 0, None)  # Ensure non-negative

    def estimate_sprint_completion_probability(self, planned_sp: int,
                                               confidence_level: float = 0.80) -> float:
        """
        Estimate probability that team can complete planned story points.
        
        Args:
            planned_sp: Number of story points planned for sprint
            confidence_level: Confidence level for prediction
            
        Returns:
            Probability of success (0-1)
        """
        prediction = self.predict_velocity(confidence_level)
        next_mean = prediction["point_estimate"]
        next_std = max(1, self.volatility)
        
        # P(X >= planned_sp) where X ~ N(mean, std)
        z = (planned_sp - next_mean) / next_std
        probability = 1 - stats.norm.cdf(z)
        
        return max(0, min(1, probability))

    def get_safe_velocity_estimate(self, risk_tolerance: float = 0.20) -> int:
        """
        Get "safe" velocity that team can achieve with high confidence.
        
        Safe velocity accounts for risk: 80% chance of success.
        
        Args:
            risk_tolerance: Acceptable failure rate (0.20 = 20% acceptable failure)
            
        Returns:
            Conservative story point estimate
        """
        prediction = self.predict_velocity(confidence_level=1 - risk_tolerance)
        # Use lower bound as safe estimate
        return max(1, int(prediction["lower_bound"]))

    def analyze_sprint_health(self) -> Dict:
        """
        Analyze overall team health and velocity stability.
        
        Returns:
            Dict with health metrics: stability, trend direction, risk level
        """
        if len(self.data) < 3:
            return {"status": "insufficient_data", "message": "Need at least 3 historical sprints"}

        # Coefficient of variation (volatility relative to mean)
        cv = self.volatility / max(1, self.baseline_velocity)
        
        if cv < 0.15:
            stability = "High"
            stability_score = 0.9
        elif cv < 0.35:
            stability = "Moderate"
            stability_score = 0.6
        else:
            stability = "Low"
            stability_score = 0.3

        # Trend direction
        if abs(self.trend) < 0.5:
            trend_dir = "Stable"
        elif self.trend > 0:
            trend_dir = "Improving"
        else:
            trend_dir = "Declining"

        # Risk assessment
        if stability_score > 0.8 and self.trend >= 0:
            risk_level = "Low"
        elif stability_score > 0.5 or (stability_score > 0.3 and self.trend >= 0):
            risk_level = "Medium"
        else:
            risk_level = "High"

        return {
            "baseline_velocity": round(self.baseline_velocity, 1),
            "volatility": round(self.volatility, 2),
            "stability": stability,
            "stability_score": round(stability_score, 2),
            "trend": trend_dir,
            "trend_magnitude": round(self.trend, 3),
            "risk_level": risk_level,
            "coefficient_of_variation": round(cv, 3),
        }

    def analyze_safety_impact(self, total_safety_critical_points: int = 50) -> Dict:
        """
        Analyze how velocity predictions impact safety-critical delivery milestones.
        Specifically evaluates ASIL-C/D feature delivery timelines.
        
        Args:
            total_safety_critical_points: Total story points for ASIL-C/D tasks
            
        Returns:
            Dict with safety delivery analysis and recommendations
        """
        prediction = self.predict_velocity(confidence_level=0.80)
        baseline = self.baseline_velocity
        
        # Calculate sprints needed at different confidence levels
        sprints_80 = total_safety_critical_points / max(1, prediction["point_estimate"])
        sprints_safe = total_safety_critical_points / max(1, prediction["lower_bound"])
        sprints_optimistic = total_safety_critical_points / max(1, prediction["upper_bound"])
        
        # Probability of completing safety tasks on time (assuming 5 sprints target)
        target_sprints = 5
        required_per_sprint = total_safety_critical_points / target_sprints
        safety_completion_prob = self.estimate_sprint_completion_probability(
            required_per_sprint, confidence_level=0.80
        )
        
        # Risk assessment for safety delivery
        if safety_completion_prob > 0.85:
            safety_status = "🟢 SAFE - High confidence in safety milestone delivery"
            risk_color = "green"
        elif safety_completion_prob > 0.70:
            safety_status = "🟡 CAUTION - Moderate risk to safety deadline"
            risk_color = "orange"
        elif safety_completion_prob > 0.50:
            safety_status = "🔴 AT RISK - Safety deadline in jeopardy"
            risk_color = "red"
        else:
            safety_status = "🚨 CRITICAL - Safety deadline highly unlikely to be met"
            risk_color = "darkred"
        
        return {
            "status": safety_status,
            "risk_color": risk_color,
            "total_safety_points": total_safety_critical_points,
            "sprints_needed_80_confidence": round(sprints_80, 1),
            "sprints_needed_safe": round(sprints_safe, 1),
            "sprints_needed_optimistic": round(sprints_optimistic, 1),
            "completion_probability": round(safety_completion_prob * 100, 1),
            "recommendation": (
                "✓ Maintain current pace" if safety_completion_prob > 0.85 else
                "⚠ Monitor closely, consider adding resources" if safety_completion_prob > 0.70 else
                "🚨 URGENT: Add resources or adjust scope to meet safety deadline"
            )
        }

    def generate_velocity_report(self, planned_sp_options: List[int] = None) -> pd.DataFrame:
        """
        Generate comprehensive velocity forecast report.
        
        Args:
            planned_sp_options: List of story point options to evaluate (default: [30, 35, 40, 45, 50])
            
        Returns:
            DataFrame with forecast for each option
        """
        if planned_sp_options is None:
            planned_sp_options = [30, 35, 40, 45, 50]

        report_rows = []
        
        for planned_sp in planned_sp_options:
            prob_success = self.estimate_sprint_completion_probability(planned_sp, confidence_level=0.80)
            
            # Risk category
            if prob_success > 0.80:
                risk_category = "Low Risk"
            elif prob_success > 0.60:
                risk_category = "Medium Risk"
            elif prob_success > 0.40:
                risk_category = "High Risk"
            else:
                risk_category = "Very High Risk"

            report_rows.append({
                "PlannedSP": planned_sp,
                "SuccessProbability": round(prob_success * 100, 1),
                "RiskCategory": risk_category,
                "Recommendation": "✓ Safe" if prob_success > 0.80 else (
                    "⚠ Caution" if prob_success > 0.60 else "✗ High Risk"
                ),
            })

        return pd.DataFrame(report_rows)

    def plot_velocity_forecast(self, figsize: Tuple = (12, 6)):
        """
        Create clean, user-friendly visualization of historical velocity with forecast.

        Args:
            figsize: Figure size tuple

        Returns:
            matplotlib figure object
        """
        fig, ax = plt.subplots(figsize=figsize, facecolor='white')

        # Plot historical velocities with clean markers
        sprints = self.data["SprintID"].values
        completed = self.data["CompletedSP"].values

        # Clean line with subtle markers
        ax.plot(sprints, completed, 'o-', linewidth=2.5, markersize=8,
               color="#1976D2", markerfacecolor="white", markeredgecolor="#1976D2",
               markeredgewidth=2, label="Actual Velocity", alpha=0.9)

        # Add trend line with clean styling
        if len(self.data) >= 2:
            x = np.arange(len(self.data))
            y_trend = self.trend * x + self.baseline_velocity
            ax.plot(sprints, y_trend, "--", linewidth=2, color="#7B1FA2",
                   label=f"Trend ({self.trend:+.1f} SP/sprint)", alpha=0.8)

        # Add baseline with subtle styling
        ax.axhline(self.baseline_velocity, color="#388E3C", linestyle="-", linewidth=1.5, alpha=0.7,
                  label=f"Average ({self.baseline_velocity:.1f} SP)")

        # Forecast for next sprint - clean and clear
        next_sprint = sprints[-1] + 1
        prediction = self.predict_velocity(confidence_level=0.80)

        # Clean confidence range
        ax.fill_between([next_sprint - 0.3, next_sprint + 0.3],
                       prediction["lower_bound"], prediction["upper_bound"],
                       alpha=0.2, color="#FF9800", linewidth=0,
                       label="Next Sprint (80% likely)")

        # Clean point estimate marker
        ax.scatter([next_sprint], [prediction["point_estimate"]],
                  s=150, color="#D32F2F", marker="o", edgecolors="white", linewidth=2,
                  label=f"Most Likely ({prediction['point_estimate']} SP)", zorder=5)

        # Clean axis labels and title
        ax.set_xlabel("Sprint Number", fontsize=11, fontweight="medium", color="#424242")
        ax.set_ylabel("Story Points Completed", fontsize=11, fontweight="medium", color="#424242")
        ax.set_title("Sprint Velocity: Past Performance & Next Sprint Forecast",
                    fontsize=13, fontweight="bold", color="#212121", pad=15)

        # Clean legend
        ax.legend(loc="upper left", fontsize=9, framealpha=0.95, edgecolor='none',
                 bbox_to_anchor=(0, 1.02, 1, 0.1), mode="expand", ncol=2,
                 labelspacing=0.3, columnspacing=1)

        # Subtle grid
        ax.grid(True, alpha=0.2, linestyle='-', color='#E0E0E0')
        ax.set_axisbelow(True)

        # Clean axis styling
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#BDBDBD')
        ax.spines['bottom'].set_color('#BDBDBD')

        # Set reasonable y-axis limits
        y_min = max(0, min(completed) - 3)
        y_max = max(completed) + 8
        ax.set_ylim(y_min, y_max)

        # Clean x-ticks
        ax.set_xticks(sprints)
        ax.tick_params(axis='both', which='major', labelsize=10, colors='#616161')

        # Tight layout
        plt.tight_layout()

        return fig

    def plot_probability_distribution(self, figsize: Tuple = (10, 6)):
        """
        Create clean probability distribution visualization.

        Args:
            figsize: Figure size tuple

        Returns:
            matplotlib figure object
        """
        fig, ax = plt.subplots(figsize=figsize, facecolor='white')

        # Generate samples
        samples = self.get_forecast_distribution(num_samples=10000)

        # Clean histogram
        ax.hist(samples, bins=25, density=True, alpha=0.6,
               color="#2196F3", edgecolor="white", linewidth=0.5)

        # Clean normal distribution curve
        x = np.linspace(samples.min(), samples.max(), 200)
        y = stats.norm.pdf(x, self.baseline_velocity + self.trend, self.volatility)
        ax.plot(x, y, "-", linewidth=2.5, color="#0D47A1", alpha=0.9, label="Expected Pattern")

        # Clean percentile lines
        percentiles = [50, 80, 90]
        colors = ["#4CAF50", "#FF9800", "#F44336"]
        labels = ["50% likely (median)", "80% likely (safe bet)", "90% likely (optimistic)"]

        for p, color, label in zip(percentiles, colors, labels):
            p_value = np.percentile(samples, p)
            ax.axvline(p_value, color=color, linestyle="-", linewidth=2, alpha=0.8, label=label)

        # Clean baseline reference
        ax.axvline(self.baseline_velocity, color="#7B1FA2", linestyle="--", linewidth=1.5, alpha=0.7,
                  label=f"Average ({self.baseline_velocity:.1f} SP)")

        # Clean axis labels and title
        ax.set_xlabel("Story Points Team Might Complete", fontsize=11, fontweight="medium", color="#424242")
        ax.set_ylabel("Probability Density", fontsize=11, fontweight="medium", color="#424242")
        ax.set_title("Next Sprint: What Are Our Chances?", fontsize=13, fontweight="bold", color="#212121", pad=15)

        # Clean legend
        ax.legend(loc="upper right", fontsize=9, framealpha=0.95, edgecolor='none',
                 labelspacing=0.3, handlelength=1.5)

        # Subtle grid
        ax.grid(True, alpha=0.2, linestyle='-', color='#E0E0E0')
        ax.set_axisbelow(True)

        # Clean axis styling
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#BDBDBD')
        ax.spines['bottom'].set_color('#BDBDBD')

        # Clean ticks
        ax.tick_params(axis='both', which='major', labelsize=10, colors='#616161')

        # Tight layout
        plt.tight_layout()

        return fig


if __name__ == "__main__":
    # Example usage
    from synthetic_data_generator import SyntheticDataGenerator
    
    generator = SyntheticDataGenerator(seed=42)
    dataset = generator.generate_complete_project_dataset()
    
    predictor = VelocityPredictor(dataset["historical_sprints"])
    
    print("VELOCITY PREDICTION ANALYSIS")
    print("=" * 60)
    
    prediction = predictor.predict_velocity(confidence_level=0.80)
    print(f"\nNext Sprint Velocity Forecast (80% confidence):")
    for key, value in prediction.items():
        print(f"  {key}: {value}")
    
    print(f"\nSprint Health Analysis:")
    health = predictor.analyze_sprint_health()
    for key, value in health.items():
        print(f"  {key}: {value}")
    
    print(f"\nVelocity Planning Report:")
    report = predictor.generate_velocity_report()
    print(report)
    
    safe_velocity = predictor.get_safe_velocity_estimate(risk_tolerance=0.20)
    print(f"\nSafe Velocity (80% confidence): {safe_velocity} SP")
