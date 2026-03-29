"""
Test Validation Module
Validates velocity prediction accuracy using a rolling-window approach.

Tests:
1. CI CHECK: Does actual velocity fall within 80% confidence interval
2. BASELINE COMPARISON: CI method vs simple rolling average accuracy
3. CI WIDTH CHECK: Is CI width reasonable (5-30 SP range)
"""

import sys
from pathlib import Path

# Add backend root to path
backend_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_root))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from src.data.synthetic_data_generator import SyntheticDataGenerator
from src.modules.velocity_predictor import VelocityPredictor
from typing import Dict, List, Tuple


class VelocityValidator:
    """Validates velocity prediction accuracy."""
    
    def __init__(self, num_sprints: int = 20, seed: int = 42):
        self.num_sprints = num_sprints
        self.seed = seed
        self.historical_sprints = None
        self.predictions = []
        self.chart_data = {
            'sprints': [],
            'actuals': [],
            'ci_lower': [],
            'ci_upper': [],
            'ci_midpoint': []
        }
    
    def generate_sprint_data(self):
        """Generate 20 sprints of historical data with seed=42."""
        print(f"\n{'='*100}")
        print(f"VELOCITY PREDICTION VALIDATION TEST")
        print(f"{'='*100}\n")
        print(f"Generating {self.num_sprints} sprints of synthetic data (seed={self.seed})...")
        
        generator = SyntheticDataGenerator(seed=self.seed)
        dataset = generator.generate_complete_project_dataset(
            project_name="Validation Project",
            team_size=12,
            num_stories=35,
            num_historical_sprints=self.num_sprints
        )
        
        self.historical_sprints = dataset['historical_sprints'].copy()
        print(f"✓ Generated {len(self.historical_sprints)} sprints")
        return self.historical_sprints
    
    def run_predictions(self, lookback_sprints: int = 5):
        """
        Predict sprints 18, 19, 20 using rolling window with lookback=5.
        """
        print(f"\nRunning predictions with lookback={lookback_sprints} for sprints 18, 19, 20...")
        
        prediction_sprints = [18, 19, 20]  # 1-indexed
        
        for pred_sprint in prediction_sprints:
            sprint_idx = pred_sprint - 1  # Convert to 0-indexed
            
            if sprint_idx < lookback_sprints:
                print(f"  Sprint {pred_sprint}: Skipped (not enough historical data)")
                continue
            
            # Get historical data up to (but not including) this sprint
            historical_data = self.historical_sprints.iloc[:sprint_idx]
            actual_velocity = self.historical_sprints.iloc[sprint_idx]['CompletedSP']
            
            # Initialize predictor
            predictor = VelocityPredictor(historical_data, lookback_sprints=lookback_sprints)
            
            # Get prediction with 80% CI
            prediction = predictor.predict_velocity(confidence_level=0.80)
            
            ci_lower = prediction['lower_bound']
            ci_upper = prediction['upper_bound']
            ci_midpoint = (ci_lower + ci_upper) / 2
            
            # Check if actual falls within CI
            within_ci = ci_lower <= actual_velocity <= ci_upper
            
            # Calculate errors
            ci_method_error = abs(actual_velocity - ci_midpoint)
            simple_avg = historical_data.tail(lookback_sprints)['CompletedSP'].mean()
            simple_avg_error = abs(actual_velocity - simple_avg)
            
            # CI width check
            ci_width = ci_upper - ci_lower
            width_valid = 5 <= ci_width <= 30
            
            pred_result = {
                'Sprint': pred_sprint,
                'Actual': actual_velocity,
                'CI Lower': ci_lower,
                'CI Upper': ci_upper,
                'CI Midpoint': ci_midpoint,
                'CI Width': ci_width,
                'Within CI': within_ci,
                'CI Method Error': ci_method_error,
                'Simple Avg': simple_avg,
                'Simple Avg Error': simple_avg_error,
                'Width Valid': width_valid
            }
            
            self.predictions.append(pred_result)
            
            # Store for chart
            self.chart_data['sprints'].append(pred_sprint)
            self.chart_data['actuals'].append(actual_velocity)
            self.chart_data['ci_lower'].append(ci_lower)
            self.chart_data['ci_upper'].append(ci_upper)
            self.chart_data['ci_midpoint'].append(ci_midpoint)
    
    def print_results_table(self):
        """Print detailed results table."""
        print("\n" + "="*100)
        print("VELOCITY PREDICTION RESULTS")
        print("="*100)
        
        if not self.predictions:
            print("No predictions to display")
            return
        
        results_df = pd.DataFrame(self.predictions)
        
        # Format for display
        display_df = results_df[['Sprint', 'Actual', 'CI Lower', 'CI Upper', 'Within CI', 
                                 'CI Method Error', 'Simple Avg Error']].copy()
        
        display_df['Actual'] = display_df['Actual'].round(2)
        display_df['CI Lower'] = display_df['CI Lower'].round(2)
        display_df['CI Upper'] = display_df['CI Upper'].round(2)
        display_df['CI Method Error'] = display_df['CI Method Error'].round(2)
        display_df['Simple Avg Error'] = display_df['Simple Avg Error'].round(2)
        display_df['Within CI'] = display_df['Within CI'].apply(lambda x: '✓' if x else '✗')
        
        print()
        print(display_df.to_string(index=False))
        print()
    
    def print_summary(self):
        """Print summary statistics."""
        print("\n" + "="*100)
        print("VALIDATION SUMMARY")
        print("="*100)
        
        if not self.predictions:
            print("No predictions to summarize")
            return
        
        results_df = pd.DataFrame(self.predictions)
        
        # CI CHECK
        ci_check_count = results_df['Within CI'].sum()
        total_predictions = len(results_df)
        ci_check_pct = (ci_check_count / total_predictions * 100) if total_predictions > 0 else 0
        
        print(f"\n✓ CI CHECK:")
        print(f"  {ci_check_count}/{total_predictions} predictions fall within 80% CI ({ci_check_pct:.0f}%)")
        print(f"  Target: 80% of predictions within CI")
        
        # BASELINE COMPARISON
        ci_avg_error = results_df['CI Method Error'].mean()
        simple_avg_error = results_df['Simple Avg Error'].mean()
        ci_wins = (results_df['CI Method Error'] < results_df['Simple Avg Error']).sum()
        
        print(f"\n✓ BASELINE COMPARISON:")
        print(f"  CI Method Average Error:     {ci_avg_error:.2f} SP")
        print(f"  Simple Average Error:        {simple_avg_error:.2f} SP")
        print(f"  Winner: {'CI Method' if ci_avg_error < simple_avg_error else 'Simple Average'}")
        print(f"  CI method wins: {ci_wins}/{total_predictions} predictions")
        error_reduction = ((simple_avg_error - ci_avg_error) / simple_avg_error * 100) if simple_avg_error > 0 else 0
        print(f"  Error reduction: {error_reduction:.1f}%")
        
        # CI WIDTH CHECK
        width_check_count = results_df['Width Valid'].sum()
        width_check_pct = (width_check_count / total_predictions * 100) if total_predictions > 0 else 0
        avg_width = results_df['CI Width'].mean()
        
        print(f"\n✓ CI WIDTH CHECK:")
        print(f"  {width_check_count}/{total_predictions} CIs have reasonable width 5-30 SP ({width_check_pct:.0f}%)")
        print(f"  Average CI width: {avg_width:.1f} SP")
        
        # OVERALL STATUS
        print(f"\n" + "="*100)
        print("OVERALL VALIDATION STATUS")
        print("="*100)
        
        all_valid = (ci_check_pct >= 70) and (ci_avg_error < simple_avg_error) and (width_check_pct >= 80)
        
        if all_valid:
            print("✓ VALIDATION PASSED - Velocity predictor is working correctly")
        else:
            print("✗ VALIDATION FAILED - Issues detected:")
            if ci_check_pct < 70:
                print(f"  - CI coverage too low: {ci_check_pct:.0f}% (target: ≥70%)")
            if ci_avg_error >= simple_avg_error:
                print(f"  - CI method not better than baseline")
            if width_check_pct < 80:
                print(f"  - CI width unreasonable: {width_check_pct:.0f}% valid (target: ≥80%)")
        
        print("="*100 + "\n")
    
    def create_chart(self, output_path: str = "tests/validation_chart.png"):
        """Create validation chart and save to file."""
        if not self.predictions:
            print(f"No predictions to chart")
            return
        
        print(f"\nGenerating validation chart...")
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        sprints = self.chart_data['sprints']
        actuals = self.chart_data['actuals']
        ci_lower = self.chart_data['ci_lower']
        ci_upper = self.chart_data['ci_upper']
        ci_midpoint = self.chart_data['ci_midpoint']
        
        # Plot CI as shaded area
        ax.fill_between(sprints, ci_lower, ci_upper, alpha=0.3, color='blue', label='80% Confidence Interval')
        
        # Plot CI midpoint (center of CI) as line
        ax.plot(sprints, ci_midpoint, 'b-', linewidth=2, label='CI Midpoint Prediction')
        
        # Plot actual velocity as red dots
        ax.scatter(sprints, actuals, color='red', s=100, zorder=5, label='Actual Velocity')
        
        # For comparison, calculate simple average predictions and plot
        if len(sprints) > 1:
            simple_avg_values = []
            for i, sprint in enumerate(sprints):
                # Simple avg from previous lookback sprints
                if i > 0:
                    simple_avg = np.mean(actuals[:i])
                else:
                    simple_avg = actuals[0]
                simple_avg_values.append(simple_avg)
            
            ax.plot(sprints, simple_avg_values, 'o--', color='orange', linewidth=2, 
                   markersize=6, label='Simple Average Prediction')
        
        # Formatting
        ax.set_xlabel('Sprint Number', fontsize=12, fontweight='bold')
        ax.set_ylabel('Completed Story Points', fontsize=12, fontweight='bold')
        ax.set_title('Velocity Prediction Validation\n80% CI vs Actual Performance', 
                    fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best', fontsize=11)
        
        # Set integer x-axis for sprints
        ax.set_xticks(sprints)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Chart saved to {output_path}")
        plt.close()


def main():
    """Main function to run velocity validation tests."""
    
    # Initialize validator with 20 sprints and seed=42
    validator = VelocityValidator(num_sprints=20, seed=42)
    
    # Generate sprint data
    validator.generate_sprint_data()
    
    # Run predictions for sprints 18, 19, 20 with lookback=5
    validator.run_predictions(lookback_sprints=5)
    
    # Print results
    validator.print_results_table()
    validator.print_summary()
    
    # Create and save chart
    validator.create_chart(output_path="tests/validation_chart.png")


if __name__ == "__main__":
    main()
