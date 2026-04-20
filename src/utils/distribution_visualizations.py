"""
Distribution Visualization Module
Generates illustrative figures for random distributions used in the Automotive DSS.
Includes visualizations for:
- Gamma distribution (story points)
- Normal distribution (velocity prediction)
- Monte Carlo simulation results
- Confidence intervals
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats
from typing import Tuple, Dict
import seaborn as sns


class DistributionVisualizer:
    """Generate publication-quality visualizations of distributions."""
    
    def __init__(self, style: str = "seaborn-v0_8-darkgrid"):
        """Initialize visualizer with matplotlib style."""
        plt.style.use(style)
        self.colors = {
            "primary": "#2E86AB",
            "secondary": "#A23B72",
            "success": "#06A77D",
            "warning": "#F18F01",
            "danger": "#C73E1D"
        }
    
    def plot_gamma_distribution_story_points(
        self,
        alpha: float = 2.5,
        beta: float = 8.0,
        max_sp: int = 100,
        num_samples: int = 5000
    ) -> Tuple[plt.Figure, np.ndarray]:
        """
        Visualize Gamma distribution used for story points generation.
        
        The Gamma distribution (α=2.5, β=8.0) provides realistic story point
        estimates that match automotive project characteristics.
        
        Args:
            alpha: Shape parameter (concentration)
            beta: Scale parameter
            max_sp: Maximum story points to display
            num_samples: Number of samples to generate
            
        Returns:
            Figure object and generated samples
        """
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Generate samples
        samples = np.random.gamma(alpha, beta, num_samples)
        samples = samples[samples <= max_sp]  # Filter to reasonable range
        
        # Left: Histogram with PDF overlay
        ax1 = axes[0]
        counts, bins, patches = ax1.hist(
            samples,
            bins=50,
            density=True,
            alpha=0.7,
            color=self.colors["primary"],
            edgecolor="black",
            label="Simulated Data (n=5000)"
        )
        
        # Overlay theoretical PDF
        x = np.linspace(0, max_sp, 200)
        pdf = stats.gamma.pdf(x, a=alpha, scale=beta)
        ax1.plot(x, pdf, color=self.colors["secondary"], linewidth=2.5, label="Gamma PDF")
        
        ax1.set_xlabel("Story Points", fontsize=12, fontweight="bold")
        ax1.set_ylabel("Probability Density", fontsize=12, fontweight="bold")
        ax1.set_title("Gamma Distribution: Story Points Generation\n(α=2.5, β=8.0)",
                     fontsize=13, fontweight="bold")
        ax1.legend(fontsize=10)
        ax1.grid(alpha=0.3)
        
        # Right: CDF
        ax2 = axes[1]
        sorted_samples = np.sort(samples)
        cdf = np.arange(1, len(sorted_samples) + 1) / len(sorted_samples)
        ax2.plot(sorted_samples, cdf, linewidth=2.5, color=self.colors["primary"],
                label="Empirical CDF")
        
        # Theoretical CDF
        x = np.linspace(0, max_sp, 200)
        theoretical_cdf = stats.gamma.cdf(x, a=alpha, scale=beta)
        ax2.plot(x, theoretical_cdf, linestyle="--", linewidth=2.5, 
                color=self.colors["secondary"], label="Theoretical CDF")
        
        ax2.set_xlabel("Story Points", fontsize=12, fontweight="bold")
        ax2.set_ylabel("Cumulative Probability", fontsize=12, fontweight="bold")
        ax2.set_title("Cumulative Distribution Function (CDF)\nStory Points",
                     fontsize=13, fontweight="bold")
        ax2.legend(fontsize=10)
        ax2.grid(alpha=0.3)
        
        plt.tight_layout()
        return fig, samples
    
    def plot_normal_distribution_velocity(
        self,
        mean: float = 22.2,
        std: float = 9.7,
        sprints_range: int = 60
    ) -> plt.Figure:
        """
        Visualize Normal distribution used for velocity prediction.
        
        Args:
            mean: Mean velocity (story points)
            std: Standard deviation
            sprints_range: Range to display (±)
            
        Returns:
            Figure object
        """
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Generate sample velocities
        velocities = np.random.normal(mean, std, 10000)
        velocities = velocities[velocities >= 0]
        
        # Top-left: PDF with samples
        ax1 = axes[0, 0]
        ax1.hist(velocities, bins=40, density=True, alpha=0.6, 
                color=self.colors["primary"], edgecolor="black", label="Simulated")
        
        x = np.linspace(max(0, mean - 4*std), mean + 4*std, 200)
        pdf = stats.norm.pdf(x, mean, std)
        ax1.plot(x, pdf, color=self.colors["secondary"], linewidth=2.5, label="Normal PDF")
        ax1.axvline(mean, color=self.colors["success"], linestyle="--", linewidth=2, 
                   label=f"Mean = {mean:.1f}")
        ax1.set_xlabel("Velocity (Story Points)", fontsize=11, fontweight="bold")
        ax1.set_ylabel("Probability Density", fontsize=11, fontweight="bold")
        ax1.set_title("Velocity Forecast Distribution\nN(22.2, 9.7)",
                     fontsize=12, fontweight="bold")
        ax1.legend(fontsize=9)
        ax1.grid(alpha=0.3)
        
        # Top-right: Q-Q plot
        ax2 = axes[0, 1]
        stats.probplot(velocities, dist="norm", plot=ax2)
        ax2.set_title("Q-Q Plot: Normality Check", fontsize=12, fontweight="bold")
        ax2.grid(alpha=0.3)
        
        # Bottom-left: Confidence intervals
        ax3 = axes[1, 0]
        confidence_levels = [0.68, 0.80, 0.90, 0.95, 0.99]
        intervals = []
        labels = []
        
        for conf in confidence_levels:
            z_score = stats.norm.ppf((1 + conf) / 2)
            margin = z_score * std
            lower = mean - margin
            upper = mean + margin
            intervals.append((lower, upper))
            labels.append(f"{int(conf*100)}%")
        
        # Plot confidence bands
        for i, (label, (lower, upper)) in enumerate(zip(labels, intervals)):
            y_pos = len(confidence_levels) - i - 1
            ax3.barh(y_pos, upper - lower, left=lower, height=0.6,
                    color=self.colors["primary"], alpha=0.7 - i*0.1, edgecolor="black")
            ax3.text(mean, y_pos, f"  {lower:.1f} - {upper:.1f}", 
                    va="center", fontsize=9, fontweight="bold")
        
        ax3.axvline(mean, color=self.colors["secondary"], linestyle="--", linewidth=2)
        ax3.set_yticks(range(len(labels)))
        ax3.set_yticklabels(labels)
        ax3.set_xlabel("Story Points", fontsize=11, fontweight="bold")
        ax3.set_ylabel("Confidence Level", fontsize=11, fontweight="bold")
        ax3.set_title("Velocity Prediction: Confidence Intervals", fontsize=12, fontweight="bold")
        ax3.grid(alpha=0.3, axis="x")
        
        # Bottom-right: Percentile plot
        ax4 = axes[1, 1]
        percentiles = np.arange(1, 100, 1)
        percentile_values = np.percentile(velocities, percentiles)
        
        ax4.fill_between(percentiles, percentile_values, alpha=0.3, color=self.colors["primary"])
        ax4.plot(percentiles, percentile_values, color=self.colors["secondary"], 
                linewidth=2.5, marker="o", markersize=3, label="Empirical percentiles")
        
        # Mark key percentiles
        key_percentiles = [10, 25, 50, 75, 90]
        for p in key_percentiles:
            val = np.percentile(velocities, p)
            ax4.plot(p, val, "o", color=self.colors["success"], markersize=8)
            ax4.text(p, val + 1, f"P{p}\n{val:.0f}", ha="center", fontsize=9)
        
        ax4.set_xlabel("Percentile", fontsize=11, fontweight="bold")
        ax4.set_ylabel("Velocity (Story Points)", fontsize=11, fontweight="bold")
        ax4.set_title("Percentile Distribution of Velocity", fontsize=12, fontweight="bold")
        ax4.grid(alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def plot_monte_carlo_simulation(
        self,
        baseline: float = 22.2,
        volatility: float = 9.7,
        num_samples: int = 5000,
        trend: float = -1.824
    ) -> plt.Figure:
        """
        Visualize Monte Carlo simulation results for velocity forecasting.
        
        Args:
            baseline: Baseline velocity
            volatility: Velocity volatility (std dev)
            num_samples: Number of MC samples
            trend: Velocity trend (SP per sprint)
            
        Returns:
            Figure object
        """
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Generate MC samples
        next_mean = baseline + trend
        mc_samples = np.random.normal(next_mean, volatility, num_samples)
        mc_samples = np.clip(mc_samples, 0, None)
        
        # Top-left: Histogram of MC samples
        ax1 = axes[0, 0]
        ax1.hist(mc_samples, bins=60, density=True, alpha=0.7, 
                color=self.colors["primary"], edgecolor="black")
        ax1.axvline(np.mean(mc_samples), color=self.colors["success"], 
                   linestyle="--", linewidth=2.5, label=f"μ = {np.mean(mc_samples):.1f}")
        ax1.axvline(np.median(mc_samples), color=self.colors["warning"], 
                   linestyle=":", linewidth=2.5, label=f"Median = {np.median(mc_samples):.1f}")
        ax1.set_xlabel("Velocity (Story Points)", fontsize=11, fontweight="bold")
        ax1.set_ylabel("Probability Density", fontsize=11, fontweight="bold")
        ax1.set_title(f"Monte Carlo Results ({num_samples:,} samples)\nVelocity Distribution",
                     fontsize=12, fontweight="bold")
        ax1.legend(fontsize=10)
        ax1.grid(alpha=0.3)
        
        # Top-right: Convergence plot
        ax2 = axes[0, 1]
        cumulative_mean = np.cumsum(mc_samples) / np.arange(1, num_samples + 1)
        
        # Plot every 10th point to reduce clutter
        plot_indices = np.arange(0, num_samples, max(1, num_samples // 500))
        ax2.plot(plot_indices, cumulative_mean[plot_indices], color=self.colors["primary"],
                linewidth=1.5, label="Cumulative Mean")
        ax2.axhline(np.mean(mc_samples), color=self.colors["secondary"], 
                   linestyle="--", linewidth=2, label="Final Mean")
        ax2.fill_between(plot_indices,
                        np.mean(mc_samples) - np.std(mc_samples),
                        np.mean(mc_samples) + np.std(mc_samples),
                        alpha=0.2, color=self.colors["primary"], label="±1σ band")
        ax2.set_xlabel("Number of Samples", fontsize=11, fontweight="bold")
        ax2.set_ylabel("Cumulative Mean Velocity", fontsize=11, fontweight="bold")
        ax2.set_title("MC Convergence: Estimate Stability", fontsize=12, fontweight="bold")
        ax2.legend(fontsize=9)
        ax2.grid(alpha=0.3)
        
        # Bottom-left: Completion probability
        ax3 = axes[1, 0]
        planned_sps = np.arange(0, 60, 1)
        completion_probs = []
        
        for planned_sp in planned_sps:
            z = (planned_sp - np.mean(mc_samples)) / max(1, np.std(mc_samples))
            prob = 1 - stats.norm.cdf(z)
            completion_probs.append(max(0, min(1, prob)))
        
        ax3.fill_between(planned_sps, completion_probs, alpha=0.3, color=self.colors["primary"])
        ax3.plot(planned_sps, completion_probs, color=self.colors["secondary"], linewidth=2.5)
        
        # Mark key points
        for prob_level in [0.5, 0.8, 0.95]:
            idx = np.argmin(np.abs(np.array(completion_probs) - prob_level))
            ax3.plot(planned_sps[idx], completion_probs[idx], "o", 
                    color=self.colors["success"], markersize=10)
            ax3.text(planned_sps[idx], completion_probs[idx] - 0.08,
                    f"{prob_level*100:.0f}%\n{planned_sps[idx]:.0f} SP",
                    ha="center", fontsize=9, fontweight="bold")
        
        ax3.set_xlabel("Planned Story Points", fontsize=11, fontweight="bold")
        ax3.set_ylabel("Probability of Completion", fontsize=11, fontweight="bold")
        ax3.set_title("Sprint Planning: Completion Probability\nby Planned Velocity",
                     fontsize=12, fontweight="bold")
        ax3.set_ylim([0, 1.05])
        ax3.grid(alpha=0.3)
        
        # Bottom-right: Risk metrics
        ax4 = axes[1, 1]
        
        # Calculate risk metrics
        percentiles_dict = {
            "P10": np.percentile(mc_samples, 10),
            "P25": np.percentile(mc_samples, 25),
            "P50 (Median)": np.percentile(mc_samples, 50),
            "P75": np.percentile(mc_samples, 75),
            "P90": np.percentile(mc_samples, 90),
        }
        
        y_pos = np.arange(len(percentiles_dict))
        values = list(percentiles_dict.values())
        bars = ax4.barh(y_pos, values, color=self.colors["primary"], edgecolor="black", alpha=0.8)
        
        # Color code by risk level
        for i, (bar, val) in enumerate(zip(bars, values)):
            if val < baseline - volatility:
                bar.set_color(self.colors["danger"])
            elif val < baseline:
                bar.set_color(self.colors["warning"])
            else:
                bar.set_color(self.colors["success"])
            ax4.text(val + 0.5, i, f"{val:.1f}", va="center", fontsize=10, fontweight="bold")
        
        ax4.set_yticks(y_pos)
        ax4.set_yticklabels(percentiles_dict.keys(), fontsize=10)
        ax4.set_xlabel("Velocity (Story Points)", fontsize=11, fontweight="bold")
        ax4.set_title("Velocity Percentiles: Risk Assessment", fontsize=12, fontweight="bold")
        ax4.grid(alpha=0.3, axis="x")
        
        plt.tight_layout()
        return fig
    
    def plot_trend_and_volatility(
        self,
        historical_velocities: list,
        forecast_periods: int = 3
    ) -> plt.Figure:
        """
        Visualize historical velocity trend and future forecast uncertainty.
        
        Args:
            historical_velocities: List of past velocities
            forecast_periods: Number of future periods to forecast
            
        Returns:
            Figure object
        """
        fig, ax = plt.subplots(figsize=(14, 6))
        
        # Historical data
        sprints = np.arange(len(historical_velocities))
        ax.plot(sprints, historical_velocities, "o-", color=self.colors["primary"],
               linewidth=2.5, markersize=8, label="Historical Velocity")
        
        # Fit trend
        z = np.polyfit(sprints, historical_velocities, 1)
        p = np.poly1d(z)
        trend_line = p(sprints)
        ax.plot(sprints, trend_line, "--", color=self.colors["secondary"],
               linewidth=2.5, label=f"Linear Trend: {z[0]:.2f} SP/sprint")
        
        # Forecast with uncertainty bands
        volatility = np.std([historical_velocities[i] - trend_line[i] 
                           for i in range(len(historical_velocities))])
        forecast_sprints = np.arange(len(historical_velocities), 
                                     len(historical_velocities) + forecast_periods)
        forecast_velocities = p(forecast_sprints)
        
        # Multiple confidence bands
        ax.plot(forecast_sprints, forecast_velocities, "s-", color=self.colors["warning"],
               linewidth=2.5, markersize=8, label="Forecast")
        
        for i, conf in enumerate([0.68, 0.80, 0.95]):
            z_score = stats.norm.ppf((1 + conf) / 2)
            margin = z_score * volatility
            
            # Increase uncertainty with forecast distance
            distances = np.arange(1, forecast_periods + 1)
            margins = margin * np.sqrt(distances)
            
            ax.fill_between(forecast_sprints,
                           forecast_velocities - margins,
                           forecast_velocities + margins,
                           alpha=0.15 - i*0.05, color=self.colors["warning"],
                           label=f"{int(conf*100)}% Confidence")
        
        # Styling
        ax.axvline(len(historical_velocities) - 0.5, color="gray", linestyle=":",
                  linewidth=2, alpha=0.7, label="Forecast boundary")
        ax.set_xlabel("Sprint Number", fontsize=12, fontweight="bold")
        ax.set_ylabel("Velocity (Story Points)", fontsize=12, fontweight="bold")
        ax.set_title("Velocity Trend Analysis & Forecast with Uncertainty Bounds",
                    fontsize=13, fontweight="bold")
        ax.legend(fontsize=10, loc="best")
        ax.grid(alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def save_all_figures(self, output_dir: str = "./figures") -> Dict[str, str]:
        """
        Generate and save all distribution visualizations.
        
        Args:
            output_dir: Directory to save figures
            
        Returns:
            Dictionary mapping figure names to file paths
        """
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        saved_files = {}
        
        # Figure 1: Gamma Distribution
        fig1, _ = self.plot_gamma_distribution_story_points()
        path1 = os.path.join(output_dir, "01_gamma_distribution_story_points.png")
        fig1.savefig(path1, dpi=300, bbox_inches="tight")
        saved_files["Gamma Distribution (Story Points)"] = path1
        plt.close(fig1)
        
        # Figure 2: Normal Distribution (Velocity)
        fig2 = self.plot_normal_distribution_velocity()
        path2 = os.path.join(output_dir, "02_normal_distribution_velocity.png")
        fig2.savefig(path2, dpi=300, bbox_inches="tight")
        saved_files["Normal Distribution (Velocity)"] = path2
        plt.close(fig2)
        
        # Figure 3: Monte Carlo Simulation
        fig3 = self.plot_monte_carlo_simulation()
        path3 = os.path.join(output_dir, "03_monte_carlo_simulation.png")
        fig3.savefig(path3, dpi=300, bbox_inches="tight")
        saved_files["Monte Carlo Simulation"] = path3
        plt.close(fig3)
        
        # Figure 4: Trend and Volatility
        # Use example historical data
        historical = [12, 14, 18, 15, 19, 21, 20, 22, 25, 23, 24]
        fig4 = self.plot_trend_and_volatility(historical, forecast_periods=3)
        path4 = os.path.join(output_dir, "04_trend_and_volatility_forecast.png")
        fig4.savefig(path4, dpi=300, bbox_inches="tight")
        saved_files["Trend & Volatility Forecast"] = path4
        plt.close(fig4)
        
        return saved_files


if __name__ == "__main__":
    # Example usage
    visualizer = DistributionVisualizer()
    files = visualizer.save_all_figures(output_dir="./figures")
    
    print("Generated Visualizations:")
    print("-" * 60)
    for name, path in files.items():
        print(f"✓ {name}")
        print(f"  → {path}")
    print("-" * 60)
