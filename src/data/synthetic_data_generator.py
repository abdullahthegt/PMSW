"""
Synthetic Data Generator Module
Generates realistic automotive project data following the schemas defined in Section 4.
Ensures statistical fidelity and structural realism for DSS simulations.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from dataclasses import dataclass
from enum import Enum
import random


class Role(Enum):
    """Team member roles in automotive projects"""
    DEVELOPER = "Developer"
    TESTER = "Tester"
    ARCHITECT = "Architect"
    PRODUCT_OWNER = "Product Owner"
    SAFETY_MANAGER = "Safety Manager"


class Seniority(Enum):
    """Seniority levels affecting efficiency"""
    JUNIOR = "Junior"
    MID = "Mid"
    SENIOR = "Senior"


class TaskType(Enum):
    """Task types mapped to ASPICE phases"""
    REQUIREMENT = "Requirement"
    DESIGN = "Design"
    CODE = "Code"
    TEST = "Test"
    SAFETY_ANALYSIS = "Safety Analysis"
    INTEGRATION = "Integration"


class ASIL(Enum):
    """Automotive Safety Integrity Levels"""
    QM = "QM"  # Quality Management (no ASIL)
    A = "A"
    B = "B"
    C = "C"
    D = "D"  # Highest criticality


class AspiceLevel(Enum):
    """ASPICE process levels"""
    SWE_1 = "SWE.1"  # Requirement Analysis
    SWE_2 = "SWE.2"  # System Design
    SWE_3 = "SWE.3"  # Detailed Design
    SWE_4 = "SWE.4"  # Unit Implementation and Test
    SWE_5 = "SWE.5"  # Integration and Integration Test
    SWE_6 = "SWE.6"  # System Qualification Test


@dataclass
class TeamMember:
    """Team member data class"""
    id: int
    name: str
    role: Role
    seniority: Seniority
    skills: List[str]
    efficiency: float
    availability: int  # hours per week


@dataclass
class Task:
    """Task/User Story data class"""
    task_id: int
    title: str
    task_type: TaskType
    aspice_id: AspiceLevel
    asil: ASIL
    story_points: int
    estimated_hours: float
    predecessors: List[int]  # List of task IDs


@dataclass
class HistoricalSprint:
    """Historical sprint performance data"""
    sprint_id: int
    planned_sp: int
    completed_sp: int
    team_size: int
    risk_event_occurred: bool
    velocity: float


@dataclass
class Risk:
    """Risk register entry"""
    risk_id: int
    description: str
    probability: float
    impact_min: float
    impact_max: float


class SyntheticDataGenerator:
    """
    Generates synthetic automotive project datasets with statistical fidelity.
    Ensures dependencies, role constraints, and realistic distributions.
    """

    # Task distribution templates
    TASK_TEMPLATES = {
        TaskType.REQUIREMENT: ["Define requirements for", "Analyze system spec for", "Create functional spec for"],
        TaskType.DESIGN: ["Design architecture for", "Create design document for", "Specify interfaces for"],
        TaskType.CODE: ["Implement", "Develop", "Code implementation for"],
        TaskType.TEST: ["Write test cases for", "Develop test suite for", "Create validation tests for"],
        TaskType.SAFETY_ANALYSIS: ["Perform HARA for", "Create FMEA for", "Conduct safety review for"],
        TaskType.INTEGRATION: ["Integrate modules for", "Perform integration testing for", "Validate integration for"],
    }

    # Role skill mappings
    ROLE_SKILLS = {
        Role.DEVELOPER: ["C/C++", "Embedded Systems", "CAN Bus", "AUTOSAR"],
        Role.TESTER: ["Unit Test", "HIL", "VectorCast", "SIL", "Test Automation"],
        Role.ARCHITECT: ["System Design", "Architecture", "ASPICE", "Design Patterns"],
        Role.PRODUCT_OWNER: ["Requirements", "Backlog Management", "Stakeholder Management"],
        Role.SAFETY_MANAGER: ["Functional Safety", "ISO 26262", "FMEA", "ASIL Classification"],
    }

    # ASIL effort multipliers
    ASIL_EFFORT_MULTIPLIERS = {
        ASIL.QM: 1.0,
        ASIL.A: 1.2,
        ASIL.B: 1.5,
        ASIL.C: 2.0,
        ASIL.D: 3.0,
    }

    # Task type dependencies
    TASK_DEPENDENCIES = {
        TaskType.REQUIREMENT: [],
        TaskType.DESIGN: [TaskType.REQUIREMENT],
        TaskType.CODE: [TaskType.DESIGN],
        TaskType.TEST: [TaskType.CODE],
        TaskType.SAFETY_ANALYSIS: [TaskType.REQUIREMENT],
        TaskType.INTEGRATION: [TaskType.CODE, TaskType.TEST],
    }

    def __init__(self, seed: int = 42):
        """Initialize with optional random seed for reproducibility"""
        np.random.seed(seed)
        random.seed(seed)

    def generate_team_members(self, size: int = 10) -> pd.DataFrame:
        """
        Generate team members with realistic skill distributions.
        
        Args:
            size: Number of team members to generate
            
        Returns:
            DataFrame with columns: ID, Name, Role, Seniority, Skills, Efficiency, Availability
        """
        # Weighted role distribution (per report Section 4.2.1)
        roles = np.random.choice(
            list(Role),
            size=size,
            p=[0.5, 0.3, 0.1, 0.05, 0.05]  # Dev, Tester, Architect, PO, Safety Manager
        )

        seniorities = np.random.choice(
            list(Seniority),
            size=size,
            p=[0.3, 0.5, 0.2]  # Junior, Mid, Senior
        )

        team_members = []
        for i in range(size):
            member_id = i + 1
            role = roles[i]
            seniority = seniorities[i]
            
            # Generate name
            name = f"{self._get_random_name()} {self._get_random_surname()}"
            
            # Assign skills based on role
            base_skills = self.ROLE_SKILLS[role].copy()
            # Add seniority-specific skills
            if seniority == Seniority.SENIOR:
                base_skills.extend(["Leadership", "Code Review", "Mentoring"])
            elif seniority == Seniority.JUNIOR:
                base_skills.append("Eager to Learn")
            
            skills = base_skills
            
            # Efficiency multiplier based on seniority
            efficiency_mean = 1.0 if seniority == Seniority.MID else (1.15 if seniority == Seniority.SENIOR else 0.85)
            efficiency = np.random.normal(efficiency_mean, 0.1)
            efficiency = max(0.5, min(1.5, efficiency))  # Clamp to reasonable range
            
            # Availability (weekly hours, minus meetings)
            availability = int(np.random.normal(35, 5))
            availability = max(20, min(40, availability))
            
            team_members.append({
                "ID": member_id,
                "Name": name,
                "Role": role.value,
                "Seniority": seniority.value,
                "Skills": ";".join(skills),
                "Efficiency": round(efficiency, 2),
                "Availability_Hours": availability,
            })

        return pd.DataFrame(team_members)

    def generate_product_backlog(self, feature_name: str = "Adaptive Cruise Control",
                                num_stories: int = 30,
                                asil_distribution: Dict = None) -> pd.DataFrame:
        """
        Generate product backlog with realistic dependencies and effort estimates.
        Respects task type dependencies and ASIL-based complexity.
        
        Args:
            feature_name: Name of feature being developed
            num_stories: Number of user stories to generate
            asil_distribution: Custom ASIL distribution {ASIL.X: probability}
            
        Returns:
            DataFrame with task details including dependencies
        """
        if asil_distribution is None:
            asil_distribution = {
                ASIL.QM: 0.4,
                ASIL.A: 0.2,
                ASIL.B: 0.2,
                ASIL.C: 0.15,
                ASIL.D: 0.05,
            }

        asils = list(asil_distribution.keys())
        asil_probs = list(asil_distribution.values())

        tasks = []
        task_id = 1
        task_type_sequence = []

        # Remainder distribution ensures task count always matches requested total
        num_phases = 4
        base = num_stories // num_phases
        remainder = num_stories % num_phases
        phase_counts = [base + 1 if i < remainder else base for i in range(num_phases)]

        # Create V-Model structure: Requirements → Design → Code → Test
        for phase_idx, task_type in enumerate(
            [TaskType.REQUIREMENT, TaskType.DESIGN, TaskType.CODE, TaskType.TEST]
        ):
            tasks_per_phase = phase_counts[phase_idx]
            
            for j in range(tasks_per_phase):
                asil = np.random.choice(asils, p=asil_probs)
                story_points = self._generate_story_points()
                
                # Generate title
                template = random.choice(self.TASK_TEMPLATES[task_type])
                title = f"{template} {feature_name} - Component {j + 1}"
                
                # Determine predecessors based on V-Model logic
                predecessors = []
                if phase_idx > 0:
                    # Depend on previous phase tasks
                    dep_phase_count = max(1, tasks_per_phase // 2)
                    for prev_task_id in range(task_id - tasks_per_phase - dep_phase_count, task_id - tasks_per_phase):
                        if prev_task_id >= 1:
                            predecessors.append(prev_task_id)
                
                # Estimate hours: SP * 8 hours * ASIL overhead * probabilistic noise
                base_hours = story_points * 8
                asil_factor = self.ASIL_EFFORT_MULTIPLIERS[asil]
                # Lognormal noise simulates probabilistic calibration uncertainty in SP-to-hours conversion
                noise = np.random.lognormal(mean=0.0, sigma=0.2)
                estimated_hours = base_hours * asil_factor * noise
                
                # Map to ASPICE level
                type_to_aspice = {
                    TaskType.REQUIREMENT: AspiceLevel.SWE_1,
                    TaskType.DESIGN: AspiceLevel.SWE_3,
                    TaskType.CODE: AspiceLevel.SWE_4,
                    TaskType.TEST: AspiceLevel.SWE_5,
                    TaskType.SAFETY_ANALYSIS: AspiceLevel.SWE_1,
                    TaskType.INTEGRATION: AspiceLevel.SWE_5,
                }
                
                tasks.append({
                    "TaskID": task_id,
                    "Title": title,
                    "Type": task_type.value,
                    "ASPICE_Level": type_to_aspice[task_type].value,
                    "ASIL": asil.value,
                    "StoryPoints": story_points,
                    "EstimatedHours": round(estimated_hours, 1),
                    "Predecessors": ";".join(map(str, predecessors)) if predecessors else "None",
                })
                
                task_id += 1

        return pd.DataFrame(tasks)

    def generate_historical_sprints(self, num_sprints: int = 10,
                                   team_size: int = 7,
                                   base_velocity: float = 40.0) -> pd.DataFrame:
        """
        Generate historical sprint data for velocity prediction training.
        Includes realistic variance and occasional risk events.
        
        Args:
            num_sprints: Number of historical sprints
            team_size: Average team size
            base_velocity: Initial velocity estimate
            
        Returns:
            DataFrame with historical sprint metrics
        """
        sprints = []
        current_velocity = base_velocity
        velocity_trend = np.random.normal(0, 2)  # Trend up or down

        for sprint_id in range(1, num_sprints + 1):
            # Trend analysis: slight improvement or degradation
            current_velocity += velocity_trend + np.random.normal(0, 1)
            current_velocity = max(10, min(80, current_velocity))  # Realistic bounds
            
            planned_sp = int(current_velocity + np.random.normal(0, 3))
            planned_sp = max(5, min(100, planned_sp))
            
            # 80% of the time, team completes close to planned
            # 20% risk events disrupt completion (Bernoulli p=0.2)
            risk_occurred = np.random.random() < 0.2
            
            if risk_occurred:
                # Risk impact: 20-60% reduction in velocity
                impact = np.random.uniform(0.2, 0.6)
                completed_sp = int(planned_sp * (1 - impact))
            else:
                # Normal variance: ±10% of planned
                completed_sp = int(planned_sp * np.random.normal(1.0, 0.1))
            
            completed_sp = max(0, min(planned_sp, completed_sp))
            
            # Slight team size variation
            actual_team_size = max(3, int(team_size + np.random.normal(0, 1)))
            
            velocity = completed_sp / sprint_id  # Cumulative velocity metric
            
            sprints.append({
                "SprintID": sprint_id,
                "PlannedSP": planned_sp,
                "CompletedSP": completed_sp,
                "TeamSize": actual_team_size,
                "RiskEventOccurred": risk_occurred,
                "Velocity": round(velocity, 2),
            })

        return pd.DataFrame(sprints)

    def generate_risk_register(self, num_risks: int = 10) -> pd.DataFrame:
        """
        Generate risk register for Monte Carlo simulation.
        Uses Beta distribution for probabilities and realistic impacts.
        
        Args:
            num_risks: Number of risks to generate
            
        Returns:
            DataFrame with risk details
        """
        risk_descriptions = [
            "HIL Bench Hardware Failure",
            "Sensor Hardware Delay",
            "Supply Chain Delay",
            "Integration Defect Discovery",
            "Safety Review Rejection",
            "CAN Bus Communication Issue",
            "Compiler/Tool Compatibility",
            "Resource Unavailability (Key Expert)",
            "Requirement Change Request",
            "Test Environment Setup Failure",
            "Automotive Safety Compliance Audit",
            "Third-party Library Issue",
        ]

        risks = []
        for risk_id in range(1, min(num_risks + 1, len(risk_descriptions) + 1)):
            description = risk_descriptions[risk_id - 1]
            
            # Beta distribution for probability (alpha=2, beta=5)
            probability = np.random.beta(2, 5)
            
            # Impact as percentage of sprint effort
            impact_min = np.random.uniform(0.1, 0.3)
            impact_max = np.random.uniform(0.3, 1.0)
            
            risks.append({
                "RiskID": risk_id,
                "Description": description,
                "Probability": round(probability, 3),
                "ImpactMin_Percent": round(impact_min, 2),
                "ImpactMax_Percent": round(impact_max, 2),
            })

        return pd.DataFrame(risks)

    def generate_complete_project_dataset(self,
                                         project_name: str = "Adaptive Cruise Control",
                                         team_size: int = 10,
                                         num_stories: int = 30,
                                         num_historical_sprints: int = 10) -> Dict[str, pd.DataFrame]:
        """
        Generate complete synthetic project dataset with all components.
        
        Args:
            project_name: Name of the automotive feature/project
            team_size: Size of team to generate
            num_stories: Number of backlog items
            num_historical_sprints: Historical sprints for velocity training
            
        Returns:
            Dictionary with DataFrames: team, backlog, history, risks
        """
        print(f"Generating synthetic dataset for '{project_name}'...")
        
        team_df = self.generate_team_members(team_size)
        print(f"✓ Generated {len(team_df)} team members")
        
        backlog_df = self.generate_product_backlog(project_name, num_stories)
        print(f"✓ Generated {len(backlog_df)} backlog items")
        
        history_df = self.generate_historical_sprints(num_historical_sprints, team_size)
        print(f"✓ Generated {num_historical_sprints} historical sprints")
        
        risks_df = self.generate_risk_register(10)
        print(f"✓ Generated {len(risks_df)} risks")
        
        return {
            "team": team_df,
            "backlog": backlog_df,
            "historical_sprints": history_df,
            "risks": risks_df,
        }

    # Helper methods
    @staticmethod
    def _generate_story_points() -> int:
        """Generate story points following Planning Poker sequence with Gamma distribution."""
        # Gamma distribution skewed right (many small tasks, few large ones)
        points = np.random.gamma(shape=2, scale=2)
        planning_poker = [1, 2, 3, 5, 8, 13, 20, 40, 100]
        
        # Round to nearest Planning Poker number
        closest = min(planning_poker, key=lambda x: abs(x - points))
        return closest

    @staticmethod
    def _get_random_name() -> str:
        """Generate random first name."""
        names = ["Alex", "Jordan", "Casey", "Riley", "Morgan", "Sam", "Taylor",
                "Chris", "Jamie", "Quinn", "Blake", "Drew", "Reese", "Parker"]
        return random.choice(names)

    @staticmethod
    def _get_random_surname() -> str:
        """Generate random surname."""
        surnames = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia",
                   "Miller", "Davis", "Rodriguez", "Martinez", "Chen", "Kumar",
                   "Anderson", "Taylor", "Thomas", "Moore", "Jackson", "White"]
        return random.choice(surnames)


if __name__ == "__main__":
    # Example usage
    generator = SyntheticDataGenerator(seed=42)
    dataset = generator.generate_complete_project_dataset(
        project_name="Advanced Driver Assistance System",
        team_size=12,
        num_stories=35,
        num_historical_sprints=15
    )
    
    print("\n" + "="*60)
    print("SYNTHETIC DATASET SUMMARY")
    print("="*60)
    for key, df in dataset.items():
        print(f"\n{key.upper()}:")
        print(df.head())
