"""
Comprehensive Project Validation Suite
Systematically validates all components of the Automotive DSS project.
"""

import sys
from pathlib import Path
backend_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_root))

import pandas as pd
import numpy as np
import traceback
from datetime import datetime
from src.data.synthetic_data_generator import SyntheticDataGenerator
from src.modules.velocity_predictor import VelocityPredictor
from src.modules.resource_load_analyzer import ResourceLoadAnalyzer

class ProjectValidator:
    """Comprehensive project validation framework."""
    
    def __init__(self):
        self.validation_results = []
        self.passed = 0
        self.failed = 0
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def log_test(self, test_name: str, passed: bool, message: str = ""):
        """Record validation test result."""
        result = {
            'Test': test_name,
            'Status': '✓ PASS' if passed else '✗ FAIL',
            'Message': message
        }
        self.validation_results.append(result)
        
        if passed:
            self.passed += 1
        else:
            self.failed += 1
        
        status_symbol = '✓' if passed else '✗'
        print(f"{status_symbol} {test_name}: {message}")
    
    # =========================================================================
    # SECTION 1: MODULE IMPORT TESTS
    # =========================================================================
    
    def test_imports(self):
        """Test all critical imports."""
        print("\n" + "="*80)
        print("SECTION 1: MODULE IMPORT TESTS")
        print("="*80)
        
        try:
            from src.data.synthetic_data_generator import SyntheticDataGenerator
            self.log_test("Import SyntheticDataGenerator", True)
        except Exception as e:
            self.log_test("Import SyntheticDataGenerator", False, str(e)[:50])
        
        try:
            from src.modules.velocity_predictor import VelocityPredictor
            self.log_test("Import VelocityPredictor", True)
        except Exception as e:
            self.log_test("Import VelocityPredictor", False, str(e)[:50])
        
        try:
            from src.modules.resource_load_analyzer import ResourceLoadAnalyzer
            self.log_test("Import ResourceLoadAnalyzer", True)
        except Exception as e:
            self.log_test("Import ResourceLoadAnalyzer", False, str(e)[:50])
    
    # =========================================================================
    # SECTION 2: DATA GENERATION TESTS
    # =========================================================================
    
    def test_data_generation(self):
        """Test synthetic data generation."""
        print("\n" + "="*80)
        print("SECTION 2: DATA GENERATION TESTS")
        print("="*80)
        
        try:
            generator = SyntheticDataGenerator(seed=42)
            self.log_test("Create SyntheticDataGenerator", True)
        except Exception as e:
            self.log_test("Create SyntheticDataGenerator", False, str(e)[:50])
            return
        
        try:
            dataset = generator.generate_complete_project_dataset(
                project_name="Test Project",
                team_size=10,
                num_stories=25,
                num_historical_sprints=8
            )
            self.log_test("Generate complete project dataset", True)
        except Exception as e:
            self.log_test("Generate complete project dataset", False, str(e)[:50])
            return
        
        # Validate dataset structure
        expected_keys = {'team', 'backlog', 'historical_sprints', 'risks'}
        if set(dataset.keys()) == expected_keys:
            self.log_test("Dataset contains required keys", True, f"Keys: {expected_keys}")
        else:
            missing = expected_keys - set(dataset.keys())
            self.log_test("Dataset contains required keys", False, f"Missing: {missing}")
        
        # Validate team data
        team_df = dataset['team']
        if len(team_df) == 10:
            self.log_test("Team size matches request", True, f"Generated {len(team_df)} members")
        else:
            self.log_test("Team size matches request", False, f"Expected 10, got {len(team_df)}")
        
        required_team_cols = {'ID', 'Name', 'Role', 'Seniority', 'Skills', 'Efficiency', 'Availability_Hours'}
        team_cols_present = required_team_cols.issubset(set(team_df.columns))
        self.log_test("Team DataFrame has required columns", team_cols_present, 
                     f"Columns: {set(team_df.columns)}")
        
        # Validate backlog data
        backlog_df = dataset['backlog']
        backlog_count_exact = len(backlog_df) == 25
        self.log_test("Backlog size matches request (exact)", backlog_count_exact, 
                     f"Expected 25, got {len(backlog_df)} tasks")
        
        required_backlog_cols = {'TaskID', 'Title', 'Type', 'ASIL', 'StoryPoints', 'EstimatedHours'}
        backlog_cols_present = required_backlog_cols.issubset(set(backlog_df.columns))
        self.log_test("Backlog DataFrame has required columns", backlog_cols_present,
                     f"Columns: {set(backlog_df.columns)}")
        
        # Validate historical sprints
        sprints_df = dataset['historical_sprints']
        if len(sprints_df) == 8:
            self.log_test("Historical sprints count matches request", True, f"Generated {len(sprints_df)} sprints")
        else:
            self.log_test("Historical sprints count matches request", False, f"Expected 8, got {len(sprints_df)}")
        
        # Validate risks
        risks_df = dataset['risks']
        if not risks_df.empty:
            self.log_test("Risk register generated", True, f"Generated {len(risks_df)} risks")
        else:
            self.log_test("Risk register generated", False, "Risk DataFrame is empty")
    
    # =========================================================================
    # SECTION 3: DATA INTEGRITY TESTS
    # =========================================================================
    
    def test_data_integrity(self):
        """Test data quality and consistency."""
        print("\n" + "="*80)
        print("SECTION 3: DATA INTEGRITY TESTS")
        print("="*80)
        
        try:
            generator = SyntheticDataGenerator(seed=42)
            dataset = generator.generate_complete_project_dataset(
                project_name="Integrity Test",
                team_size=10,
                num_stories=20,
                num_historical_sprints=10
            )
        except Exception as e:
            self.log_test("Generate dataset for integrity tests", False, str(e)[:50])
            return
        
        team_df = dataset['team']
        backlog_df = dataset['backlog']
        sprints_df = dataset['historical_sprints']
        
        # Check for null values
        no_nulls_team = team_df.isnull().sum().sum() == 0
        self.log_test("Team data: No null values", no_nulls_team, 
                     f"Nulls: {team_df.isnull().sum().sum()}")
        
        no_nulls_backlog = backlog_df.isnull().sum().sum() == 0
        self.log_test("Backlog data: No null values", no_nulls_backlog,
                     f"Nulls: {backlog_df.isnull().sum().sum()}")
        
        # Check efficiency values in valid range
        efficiency_valid = team_df['Efficiency'].between(0.5, 1.5).all()
        self.log_test("Team efficiency in valid range (0.5-1.5)", efficiency_valid,
                     f"Range: {team_df['Efficiency'].min():.2f}-{team_df['Efficiency'].max():.2f}")
        
        # Check availability hours
        availability_valid = team_df['Availability_Hours'].between(20, 40).all()
        self.log_test("Availability hours in valid range (20-40)", availability_valid,
                     f"Range: {team_df['Availability_Hours'].min()}-{team_df['Availability_Hours'].max()}")
        
        # Check story points positive
        sp_valid = (backlog_df['StoryPoints'] > 0).all()
        self.log_test("All story points positive", sp_valid,
                     f"Range: {backlog_df['StoryPoints'].min()}-{backlog_df['StoryPoints'].max()}")
        
        # Check ASIL values valid
        valid_asils = {'QM', 'A', 'B', 'C', 'D'}
        asil_valid = set(backlog_df['ASIL'].unique()).issubset(valid_asils)
        self.log_test("ASIL values valid", asil_valid,
                     f"Values: {set(backlog_df['ASIL'].unique())}")
        
        # Check sprint velocity data
        sprints_valid = (sprints_df['CompletedSP'] > 0).all() and (sprints_df['PlannedSP'] > 0).all()
        self.log_test("Sprint velocity data valid", sprints_valid,
                     f"Completed: {sprints_df['CompletedSP'].min()}-{sprints_df['CompletedSP'].max()}")
        
        # Check for duplicate team members
        no_duplicate_members = len(team_df) == len(team_df['Name'].unique())
        self.log_test("No duplicate team members", no_duplicate_members,
                     f"Unique: {len(team_df['Name'].unique())}/{len(team_df)}")
        
        # Check for duplicate tasks
        no_duplicate_tasks = len(backlog_df) == len(backlog_df['TaskID'].unique())
        self.log_test("No duplicate tasks", no_duplicate_tasks,
                     f"Unique: {len(backlog_df['TaskID'].unique())}/{len(backlog_df)}")
    
    # =========================================================================
    # SECTION 4: VELOCITY PREDICTOR TESTS
    # =========================================================================
    
    def test_velocity_predictor(self):
        """Test velocity prediction module."""
        print("\n" + "="*80)
        print("SECTION 4: VELOCITY PREDICTOR TESTS")
        print("="*80)
        
        try:
            generator = SyntheticDataGenerator(seed=42)
            dataset = generator.generate_complete_project_dataset(
                project_name="Predictor Test",
                team_size=10,
                num_stories=20,
                num_historical_sprints=10
            )
            historical_sprints = dataset['historical_sprints']
            self.log_test("Generate dataset for velocity tests", True)
        except Exception as e:
            self.log_test("Generate dataset for velocity tests", False, str(e)[:50])
            return
        
        try:
            predictor = VelocityPredictor(historical_sprints, lookback_sprints=3)
            self.log_test("Initialize VelocityPredictor", True)
        except Exception as e:
            self.log_test("Initialize VelocityPredictor", False, str(e)[:50])
            return
        
        try:
            prediction = predictor.predict_velocity(confidence_level=0.80)
            self.log_test("Generate velocity prediction", True)
        except Exception as e:
            self.log_test("Generate velocity prediction", False, str(e)[:50])
            return
        
        # Validate prediction structure
        required_pred_keys = {'point_estimate', 'lower_bound', 'upper_bound', 'trend'}
        pred_keys_present = required_pred_keys.issubset(set(prediction.keys()))
        self.log_test("Prediction has required keys", pred_keys_present,
                     f"Keys: {set(prediction.keys())}")
        
        # Validate CI bounds
        ci_valid = prediction['lower_bound'] <= prediction['point_estimate'] <= prediction['upper_bound']
        self.log_test("CI bounds valid (lower ≤ estimate ≤ upper)", ci_valid,
                     f"CI: [{prediction['lower_bound']:.1f}, {prediction['upper_bound']:.1f}]")
        
        # Check CI width
        ci_width = prediction['upper_bound'] - prediction['lower_bound']
        width_reasonable = 5 <= ci_width <= 30
        self.log_test("CI width reasonable (5-30 SP)", width_reasonable,
                     f"Width: {ci_width:.1f} SP")
        
        try:
            prob = predictor.estimate_sprint_completion_probability(planned_sp=40)
            prob_valid = 0 <= prob <= 1
            self.log_test("Sprint completion probability valid", prob_valid,
                         f"Probability: {prob:.1%}")
        except Exception as e:
            self.log_test("Sprint completion probability calculation", False, str(e)[:50])
        
        try:
            safe_velocity = predictor.get_safe_velocity_estimate()
            safe_valid = safe_velocity > 0
            self.log_test("Safe velocity estimate positive", safe_valid,
                         f"Safe velocity: {safe_velocity:.1f} SP")
        except Exception as e:
            self.log_test("Safe velocity estimate", False, str(e)[:50])
    
    # =========================================================================
    # SECTION 5: RESOURCE LOAD ANALYZER TESTS
    # =========================================================================
    
    def test_resource_analyzer(self):
        """Test resource allocation module."""
        print("\n" + "="*80)
        print("SECTION 5: RESOURCE LOAD ANALYZER TESTS")
        print("="*80)
        
        try:
            generator = SyntheticDataGenerator(seed=42)
            dataset = generator.generate_complete_project_dataset(
                project_name="Resource Test",
                team_size=10,
                num_stories=20,
                num_historical_sprints=5
            )
            team_df = dataset['team']
            backlog_df = dataset['backlog']
            self.log_test("Generate dataset for resource tests", True)
        except Exception as e:
            self.log_test("Generate dataset for resource tests", False, str(e)[:50])
            return
        
        try:
            analyzer = ResourceLoadAnalyzer(team_df, backlog_df)
            self.log_test("Initialize ResourceLoadAnalyzer", True)
        except Exception as e:
            self.log_test("Initialize ResourceLoadAnalyzer", False, str(e)[:50])
            return
        
        try:
            result = analyzer.allocate_resources(respect_capacity_limits=True)
            self.log_test("Execute resource allocation", True)
        except Exception as e:
            self.log_test("Execute resource allocation", False, str(e)[:50])
            return
        
        # Validate result structure
        required_result_keys = {'allocation_df', 'infeasible_tasks', 'bottleneck_analysis', 'team_status'}
        result_keys_present = required_result_keys.issubset(set(result.keys()))
        self.log_test("Allocation result has required keys", result_keys_present,
                     f"Keys: {set(result.keys())}")
        
        allocation_df = result['allocation_df']
        required_alloc_cols = {'TaskID', 'Title', 'AssignedTo', 'EstimatedHours', 'Status'}
        alloc_cols_present = required_alloc_cols.issubset(set(allocation_df.columns))
        self.log_test("Allocation DataFrame has required columns", alloc_cols_present,
                     f"Columns: {set(allocation_df.columns)}")
        
        # Check no duplicate assignments
        no_dupes = len(allocation_df) == len(allocation_df['TaskID'].unique())
        self.log_test("No duplicate task assignments", no_dupes,
                     f"Unique: {len(allocation_df['TaskID'].unique())}/{len(allocation_df)}")
        
        # Check all tasks assigned
        all_assigned = allocation_df[~allocation_df['AssignedTo'].str.contains('Unassigned', na=False)].shape[0] > 0
        self.log_test("Tasks assigned to team members", all_assigned,
                     f"Assigned: {allocation_df[~allocation_df['AssignedTo'].str.contains('Unassigned', na=False)].shape[0]}/{len(allocation_df)}")
    
    # =========================================================================
    # SECTION 6: EDGE CASE TESTS
    # =========================================================================
    
    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        print("\n" + "="*80)
        print("SECTION 6: EDGE CASE TESTS")
        print("="*80)
        
        # Test with minimum team size
        try:
            generator = SyntheticDataGenerator(seed=42)
            dataset = generator.generate_complete_project_dataset(
                project_name="Minimum Team",
                team_size=3,
                num_stories=5,
                num_historical_sprints=2
            )
            self.log_test("Handle minimum team size (3)", True,
                         f"Generated: {len(dataset['team'])} members")
        except Exception as e:
            self.log_test("Handle minimum team size (3)", False, str(e)[:50])
        
        # Test with large team size
        try:
            generator = SyntheticDataGenerator(seed=42)
            dataset = generator.generate_complete_project_dataset(
                project_name="Large Team",
                team_size=30,
                num_stories=100,
                num_historical_sprints=5
            )
            self.log_test("Handle large team size (30)", True,
                         f"Generated: {len(dataset['team'])} members")
        except Exception as e:
            self.log_test("Handle large team size (30)", False, str(e)[:50])
        
        # Test with single sprint history
        try:
            generator = SyntheticDataGenerator(seed=42)
            dataset = generator.generate_complete_project_dataset(
                project_name="Single Sprint",
                team_size=10,
                num_stories=20,
                num_historical_sprints=1
            )
            predictor = VelocityPredictor(dataset['historical_sprints'], lookback_sprints=1)
            prediction = predictor.predict_velocity(confidence_level=0.80)
            self.log_test("Handle single sprint history", True)
        except Exception as e:
            self.log_test("Handle single sprint history", False, str(e)[:50])
        
        # Test reproducibility with seed
        try:
            gen1 = SyntheticDataGenerator(seed=12345)
            dataset1 = gen1.generate_complete_project_dataset(
                project_name="Test1", team_size=10, num_stories=20, num_historical_sprints=5
            )
            
            gen2 = SyntheticDataGenerator(seed=12345)
            dataset2 = gen2.generate_complete_project_dataset(
                project_name="Test1", team_size=10, num_stories=20, num_historical_sprints=5
            )
            
            reproducible = dataset1['team']['Name'].equals(dataset2['team']['Name'])
            self.log_test("Reproducibility with same seed", reproducible)
        except Exception as e:
            self.log_test("Reproducibility with same seed", False, str(e)[:50])
    
    # =========================================================================
    # SECTION 7: INTEGRATION TESTS
    # =========================================================================
    
    def test_integration(self):
        """Test integration between modules."""
        print("\n" + "="*80)
        print("SECTION 7: INTEGRATION TESTS")
        print("="*80)
        
        try:
            # Full workflow test
            generator = SyntheticDataGenerator(seed=42)
            dataset = generator.generate_complete_project_dataset(
                project_name="Integration Test",
                team_size=12,
                num_stories=30,
                num_historical_sprints=8
            )
            
            # Test velocity prediction on historical data
            predictor = VelocityPredictor(dataset['historical_sprints'], lookback_sprints=3)
            prediction = predictor.predict_velocity(confidence_level=0.80)
            
            # Test resource allocation
            analyzer = ResourceLoadAnalyzer(dataset['team'], dataset['backlog'])
            allocation = analyzer.allocate_resources(respect_capacity_limits=True)
            
            # All steps successful
            self.log_test("Full workflow integration", True,
                         "Generated → Predicted → Allocated")
        except Exception as e:
            self.log_test("Full workflow integration", False, str(e)[:50])
        
        try:
            # Test with multiple seeds
            for seed in [1, 42, 100, 9999]:
                generator = SyntheticDataGenerator(seed=seed)
                dataset = generator.generate_complete_project_dataset(
                    project_name=f"Test {seed}",
                    team_size=10,
                    num_stories=20,
                    num_historical_sprints=5
                )
                analyzer = ResourceLoadAnalyzer(dataset['team'], dataset['backlog'])
                analyzer.allocate_resources(respect_capacity_limits=True)
            
            self.log_test("Multi-seed robustness", True,
                         "All 4 different seeds processed successfully")
        except Exception as e:
            self.log_test("Multi-seed robustness", False, str(e)[:50])
    
    # =========================================================================
    # FINAL REPORT
    # =========================================================================
    
    def generate_report(self):
        """Generate comprehensive validation report."""
        print("\n" + "="*80)
        print("COMPREHENSIVE VALIDATION REPORT")
        print("="*80)
        print(f"Timestamp: {self.timestamp}\n")
        
        # Results table
        results_df = pd.DataFrame(self.validation_results)
        print(results_df.to_string(index=False))
        
        # Summary
        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0
        
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        print(f"Total Tests: {total}")
        print(f"Passed: {self.passed} ({pass_rate:.1f}%)")
        print(f"Failed: {self.failed}")
        
        if self.failed == 0:
            print("\n✓✓✓ ALL VALIDATION TESTS PASSED ✓✓✓")
        else:
            print(f"\n✗✗✗ {self.failed} TESTS FAILED ✗✗✗")
        
        print("="*80 + "\n")
        
        return {
            'total': total,
            'passed': self.passed,
            'failed': self.failed,
            'pass_rate': pass_rate,
            'timestamp': self.timestamp
        }


def main():
    """Run comprehensive validation."""
    print("\n" + "="*80)
    print("AUTOMOTIVE DSS - COMPREHENSIVE PROJECT VALIDATION")
    print("="*80)
    
    validator = ProjectValidator()
    
    # Run all validation sections
    validator.test_imports()
    validator.test_data_generation()
    validator.test_data_integrity()
    validator.test_velocity_predictor()
    validator.test_resource_analyzer()
    validator.test_edge_cases()
    validator.test_integration()
    
    # Generate final report
    report = validator.generate_report()
    
    return report


if __name__ == "__main__":
    main()
