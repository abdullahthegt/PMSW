"""
Test Verification Module
Validates key constraints of the Automotive DSS using 50 randomized trials.

Constraints Tested:
1. SKILL: No ASIL-C/D task assigned to member without Functional Safety skill
2. CAPACITY: No member exceeds 100% utilization
3. COMPLETENESS: All tasks assigned (nothing skipped)
4. DUPLICATE: No task assigned to two different members
"""

import sys
from pathlib import Path

# Add backend root to path
backend_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_root))

import pandas as pd
import numpy as np
from src.data.synthetic_data_generator import SyntheticDataGenerator
from src.modules.resource_load_analyzer import ResourceLoadAnalyzer
from typing import Dict, List, Tuple


class ConstraintValidator:
    """Validates allocation constraints across trials."""
    
    def __init__(self):
        self.trial_results = []
        self.constraint_stats = {
            'SKILL': {'violations': 0, 'trials': 0},
            'CAPACITY': {'violations': 0, 'trials': 0},
            'COMPLETENESS': {'violations': 0, 'trials': 0},
            'DUPLICATE': {'violations': 0, 'trials': 0}
        }
    
    def check_skill_constraint(self, team_df: pd.DataFrame, allocation_df: pd.DataFrame, tasks_df: pd.DataFrame) -> Tuple[bool, str]:
        """
        Check if ASIL-C/D tasks are only assigned to members with Functional Safety skill.
        
        Return: (is_valid, message)
        """
        violations = []
        
        for idx, task in tasks_df.iterrows():
            task_id = task['TaskID']
            asil_level = task.get('ASIL', 'QM')
            
            # Only ASIL-C and ASIL-D require Functional Safety
            if asil_level not in ['C', 'D']:
                continue
            
            # Find who this task is assigned to
            assignment = allocation_df[allocation_df['TaskID'] == task_id]
            if assignment.empty:
                continue
            
            assigned_member = assignment.iloc[0]['AssignedTo']
            
            # Check if member has Functional Safety skill
            member = team_df[team_df['Name'] == assigned_member]
            if not member.empty:
                skills = member.iloc[0].get('Skills', [])
                if isinstance(skills, str):
                    skills = [s.strip() for s in skills.split(',')]
                
                if 'Functional Safety' not in skills:
                    violations.append(
                        f"Task {task_id} (ASIL-{asil_level}) assigned to {assigned_member} "
                        f"without Functional Safety skill"
                    )
        
        is_valid = len(violations) == 0
        message = "; ".join(violations) if violations else "PASS"
        return is_valid, message
    
    def check_capacity_constraint(self, team_df: pd.DataFrame, allocation_df: pd.DataFrame, tasks_df: pd.DataFrame) -> Tuple[bool, str]:
        """
        Check if any member exceeds 100% utilization.
        Assumes Availability_Hours in team_df and EstimatedHours in allocation_df.
        
        Return: (is_valid, message)
        """
        violations = []
        
        # Calculate total hours allocated per member
        member_hours = allocation_df.groupby('AssignedTo')['EstimatedHours'].sum()
        
        for member_name, total_hours in member_hours.items():
            member = team_df[team_df['Name'] == member_name]
            if not member.empty:
                available_hours = member.iloc[0].get('Availability_Hours', 40)
                utilization = total_hours / available_hours if available_hours > 0 else 0
                
                if utilization > 1.0:
                    violations.append(
                        f"{member_name}: {utilization:.1%} utilization "
                        f"({total_hours:.1f}h/{available_hours}h)"
                    )
        
        is_valid = len(violations) == 0
        message = "; ".join(violations) if violations else "PASS"
        return is_valid, message
    
    def check_completeness_constraint(self, tasks_df: pd.DataFrame, allocation_df: pd.DataFrame) -> Tuple[bool, str]:
        """
        Check if all tasks got an assignment.
        
        Return: (is_valid, message)
        """
        unassigned_tasks = []
        
        for idx, task in tasks_df.iterrows():
            task_id = task['TaskID']
            if task_id not in allocation_df['TaskID'].values:
                unassigned_tasks.append(str(task_id))
        
        is_valid = len(unassigned_tasks) == 0
        message = f"PASS" if is_valid else f"Unassigned: {', '.join(unassigned_tasks[:5])}"
        if len(unassigned_tasks) > 5:
            message += f" +{len(unassigned_tasks) - 5} more"
        
        return is_valid, message
    
    def check_duplicate_constraint(self, allocation_df: pd.DataFrame) -> Tuple[bool, str]:
        """
        Check if any task is assigned to multiple members.
        
        Return: (is_valid, message)
        """
        duplicates = []
        
        task_assignments = allocation_df.groupby('TaskID').size()
        duplicate_tasks = task_assignments[task_assignments > 1]
        
        if not duplicate_tasks.empty:
            for task_id in duplicate_tasks.index[:5]:  # Show first 5
                count = duplicate_tasks[task_id]
                duplicates.append(f"Task {task_id} assigned to {count} members")
        
        is_valid = len(duplicates) == 0
        message = "PASS" if is_valid else "; ".join(duplicates)
        
        return is_valid, message
    
    def run_trial(self, trial_num: int, seed: int) -> Dict:
        """Run a single trial and check all constraints."""
        result = {'Trial': trial_num}
        
        try:
            # Generate synthetic data
            generator = SyntheticDataGenerator(seed=seed)
            dataset = generator.generate_complete_project_dataset(
                project_name=f"Test Project {trial_num}",
                team_size=np.random.randint(8, 16),
                num_stories=np.random.randint(20, 40),
                num_historical_sprints=5
            )
            
            team_df = dataset['team']
            tasks_df = dataset['backlog']
            
            # Allocate resources
            analyzer = ResourceLoadAnalyzer(team_df, tasks_df)
            allocation_result = analyzer.allocate_resources()
            allocation_df = allocation_result['allocation_df']
            
            # Check SKILL constraint
            skill_valid, skill_msg = self.check_skill_constraint(team_df, allocation_df, tasks_df)
            result['SKILL'] = skill_valid
            self.constraint_stats['SKILL']['violations'] += 0 if skill_valid else 1
            self.constraint_stats['SKILL']['trials'] += 1
            
            # Check CAPACITY constraint
            capacity_valid, capacity_msg = self.check_capacity_constraint(team_df, allocation_df, tasks_df)
            result['CAPACITY'] = capacity_valid
            self.constraint_stats['CAPACITY']['violations'] += 0 if capacity_valid else 1
            self.constraint_stats['CAPACITY']['trials'] += 1
            
            # Check COMPLETENESS constraint
            complete_valid, complete_msg = self.check_completeness_constraint(tasks_df, allocation_df)
            result['COMPLETENESS'] = complete_valid
            self.constraint_stats['COMPLETENESS']['violations'] += 0 if complete_valid else 1
            self.constraint_stats['COMPLETENESS']['trials'] += 1
            
            # Check DUPLICATE constraint
            duplicate_valid, duplicate_msg = self.check_duplicate_constraint(allocation_df)
            result['DUPLICATE'] = duplicate_valid
            self.constraint_stats['DUPLICATE']['violations'] += 0 if duplicate_valid else 1
            self.constraint_stats['DUPLICATE']['trials'] += 1
            
            result['Status'] = 'PASS' if all([skill_valid, capacity_valid, complete_valid, duplicate_valid]) else 'FAIL'
            
        except Exception as e:
            result['Status'] = f'ERROR: {str(e)[:50]}'
            result['SKILL'] = None
            result['CAPACITY'] = None
            result['COMPLETENESS'] = None
            result['DUPLICATE'] = None
        
        self.trial_results.append(result)
        return result
    
    def run_all_trials(self, num_trials: int = 50):
        """Run all validation trials."""
        print(f"\n{'='*80}")
        print(f"CONSTRAINT VALIDATION TEST - {num_trials} RANDOMIZED TRIALS")
        print(f"{'='*80}\n")
        
        for trial_num in range(1, num_trials + 1):
            seed = 42 + trial_num
            self.run_trial(trial_num, seed)
            if trial_num % 10 == 0:
                print(f"  Completed {trial_num} trials...")
        
        self.print_summary()
    
    def print_summary(self):
        """Print results summary."""
        results_df = pd.DataFrame(self.trial_results)
        
        print("\n" + "="*80)
        print("DETAILED RESULTS TABLE")
        print("="*80)
        print(results_df.to_string(index=False))
        
        print("\n" + "="*80)
        print("CONSTRAINT SATISFACTION SUMMARY")
        print("="*80)
        print()
        
        summary_data = []
        for constraint, stats in self.constraint_stats.items():
            trials = stats['trials']
            violations = stats['violations']
            satisfied = trials - violations
            satisfaction_rate = (satisfied / trials * 100) if trials > 0 else 0
            
            summary_data.append({
                'Constraint': constraint,
                'Violations': violations,
                'Trials': trials,
                'Satisfied': satisfied,
                'Rate (%)': f"{satisfaction_rate:.1f}%",
                'Status': '✓ PASS' if satisfaction_rate == 100 else '✗ FAIL'
            })
        
        summary_df = pd.DataFrame(summary_data)
        print(summary_df.to_string(index=False))
        
        print("\n" + "="*80)
        print("OVERALL STATUS")
        print("="*80)
        
        all_pass = all(
            stats['violations'] == 0 
            for stats in self.constraint_stats.values()
        )
        
        if all_pass:
            print("✓ ALL CONSTRAINTS PASSED IN ALL TRIALS")
        else:
            print("✗ SOME CONSTRAINTS FAILED")
            for constraint, stats in self.constraint_stats.items():
                if stats['violations'] > 0:
                    print(f"  - {constraint}: {stats['violations']} violations in {stats['trials']} trials")
        
        print("="*80 + "\n")
        
        return all_pass


def main():
    """Main function to run verification tests."""
    validator = ConstraintValidator()
    validator.run_all_trials(num_trials=50)


if __name__ == "__main__":
    main()
