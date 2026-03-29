"""
Service Layer
Business logic layer that orchestrates repositories
"""

from sqlalchemy.orm import Session
from typing import Optional, List
from src.repositories import (
    TeamRepository, SprintRepository, TaskRepository,
    TeamMemberRepository, ResourceMetricsRepository
)
from src.schemas import (
    TeamCreate, SprintCreate, TaskCreate,
    TeamMemberCreate, ResourceMetricsCreate
)
from src.models import Team, Sprint, Task, TeamMember, ResourceMetrics


class TeamService:
    """Business logic for Team operations"""
    
    def __init__(self, db: Session):
        self.repository = TeamRepository(db)
        self.db = db
    
    def create_team(self, team_in: TeamCreate) -> Team:
        """Create a new team with validation"""
        existing = self.repository.get_by_name(team_in.name)
        if existing:
            raise ValueError(f"Team with name '{team_in.name}' already exists")
        return self.repository.create(team_in)
    
    def get_team(self, team_id: int) -> Optional[Team]:
        """Get a team by ID"""
        team = self.repository.get_by_id(team_id)
        if not team:
            raise ValueError(f"Team with ID {team_id} not found")
        return team
    
    def get_all_teams(self, skip: int = 0, limit: int = 100) -> List[Team]:
        """Get all teams"""
        return self.repository.get_all(skip=skip, limit=limit)
    
    def update_team(self, team_id: int, team_in: TeamCreate) -> Team:
        """Update a team"""
        team = self.repository.update(team_id, team_in)
        if not team:
            raise ValueError(f"Team with ID {team_id} not found")
        return team
    
    def delete_team(self, team_id: int) -> bool:
        """Delete a team"""
        result = self.repository.delete(team_id)
        if not result:
            raise ValueError(f"Team with ID {team_id} not found")
        return result


class SprintService:
    """Business logic for Sprint operations"""
    
    def __init__(self, db: Session):
        self.sprint_repo = SprintRepository(db)
        self.team_repo = TeamRepository(db)
        self.db = db
    
    def create_sprint(self, sprint_in: SprintCreate) -> Sprint:
        """Create a new sprint with validation"""
        # Validate team exists
        team = self.team_repo.get_by_id(sprint_in.team_id)
        if not team:
            raise ValueError(f"Team with ID {sprint_in.team_id} not found")
        
        # Validate dates
        if sprint_in.start_date >= sprint_in.end_date:
            raise ValueError("Sprint start_date must be before end_date")
        
        return self.sprint_repo.create(sprint_in)
    
    def get_sprint(self, sprint_id: int) -> Optional[Sprint]:
        """Get a sprint by ID"""
        sprint = self.sprint_repo.get_by_id(sprint_id)
        if not sprint:
            raise ValueError(f"Sprint with ID {sprint_id} not found")
        return sprint
    
    def get_team_sprints(self, team_id: int) -> List[Sprint]:
        """Get all sprints for a team"""
        team = self.team_repo.get_by_id(team_id)
        if not team:
            raise ValueError(f"Team with ID {team_id} not found")
        return self.sprint_repo.get_by_team(team_id)
    
    def get_active_sprint(self, team_id: int) -> Optional[Sprint]:
        """Get active sprint for a team"""
        return self.sprint_repo.get_active_sprint(team_id)
    
    def update_sprint(self, sprint_id: int, sprint_in: SprintCreate) -> Sprint:
        """Update a sprint"""
        sprint = self.sprint_repo.update(sprint_id, sprint_in)
        if not sprint:
            raise ValueError(f"Sprint with ID {sprint_id} not found")
        return sprint
    
    def delete_sprint(self, sprint_id: int) -> bool:
        """Delete a sprint"""
        result = self.sprint_repo.delete(sprint_id)
        if not result:
            raise ValueError(f"Sprint with ID {sprint_id} not found")
        return result


class TaskService:
    """Business logic for Task operations"""
    
    def __init__(self, db: Session):
        self.task_repo = TaskRepository(db)
        self.sprint_repo = SprintRepository(db)
        self.db = db
    
    def create_task(self, task_in: TaskCreate) -> Task:
        """Create a new task with validation"""
        # Validate sprint exists
        sprint = self.sprint_repo.get_by_id(task_in.sprint_id)
        if not sprint:
            raise ValueError(f"Sprint with ID {task_in.sprint_id} not found")
        
        return self.task_repo.create(task_in)
    
    def get_task(self, task_id: int) -> Optional[Task]:
        """Get a task by ID"""
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} not found")
        return task
    
    def get_sprint_tasks(self, sprint_id: int) -> List[Task]:
        """Get all tasks in a sprint"""
        sprint = self.sprint_repo.get_by_id(sprint_id)
        if not sprint:
            raise ValueError(f"Sprint with ID {sprint_id} not found")
        return self.task_repo.get_by_sprint(sprint_id)
    
    def get_tasks_by_status(self, sprint_id: int, status: str) -> List[Task]:
        """Get tasks by status"""
        valid_statuses = ["todo", "in_progress", "done"]
        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")
        return self.task_repo.get_by_status(sprint_id, status)
    
    def update_task(self, task_id: int, task_in: TaskCreate) -> Task:
        """Update a task"""
        task = self.task_repo.update(task_id, task_in)
        if not task:
            raise ValueError(f"Task with ID {task_id} not found")
        return task
    
    def delete_task(self, task_id: int) -> bool:
        """Delete a task"""
        result = self.task_repo.delete(task_id)
        if not result:
            raise ValueError(f"Task with ID {task_id} not found")
        return result
    
    def calculate_sprint_velocity(self, sprint_id: int) -> float:
        """Calculate velocity of a sprint (completed story points)"""
        tasks = self.task_repo.get_by_status(sprint_id, "done")
        return sum(task.story_points or 0 for task in tasks)


class TeamMemberService:
    """Business logic for TeamMember operations"""
    
    def __init__(self, db: Session):
        self.member_repo = TeamMemberRepository(db)
        self.team_repo = TeamRepository(db)
        self.db = db
    
    def add_team_member(self, member_in: TeamMemberCreate) -> TeamMember:
        """Add a new team member"""
        # Validate team exists
        team = self.team_repo.get_by_id(member_in.team_id)
        if not team:
            raise ValueError(f"Team with ID {member_in.team_id} not found")
        
        # Check if email already exists
        existing = self.member_repo.get_by_email(member_in.email)
        if existing:
            raise ValueError(f"Member with email '{member_in.email}' already exists")
        
        return self.member_repo.create(member_in)
    
    def get_team_member(self, member_id: int) -> Optional[TeamMember]:
        """Get a team member by ID"""
        member = self.member_repo.get_by_id(member_id)
        if not member:
            raise ValueError(f"Team member with ID {member_id} not found")
        return member
    
    def get_team_members(self, team_id: int) -> List[TeamMember]:
        """Get all members of a team"""
        team = self.team_repo.get_by_id(team_id)
        if not team:
            raise ValueError(f"Team with ID {team_id} not found")
        return self.member_repo.get_by_team(team_id)
    
    def update_team_member(self, member_id: int, member_in: TeamMemberCreate) -> TeamMember:
        """Update a team member"""
        member = self.member_repo.update(member_id, member_in)
        if not member:
            raise ValueError(f"Team member with ID {member_id} not found")
        return member
    
    def remove_team_member(self, member_id: int) -> bool:
        """Remove a team member"""
        result = self.member_repo.delete(member_id)
        if not result:
            raise ValueError(f"Team member with ID {member_id} not found")
        return result
    
    def calculate_team_capacity(self, team_id: int) -> float:
        """Calculate total capacity of a team (hours per day)"""
        members = self.member_repo.get_by_team(team_id)
        return sum(member.capacity for member in members)


class ResourceAnalysisService:
    """Business logic for Resource Analysis"""
    
    def __init__(self, db: Session):
        self.metrics_repo = ResourceMetricsRepository(db)
        self.sprint_repo = SprintRepository(db)
        self.member_repo = TeamMemberRepository(db)
        self.task_repo = TaskRepository(db)
        self.db = db
    
    def analyze_sprint_resources(self, sprint_id: int) -> dict:
        """Analyze resource utilization for a sprint"""
        sprint = self.sprint_repo.get_by_id(sprint_id)
        if not sprint:
            raise ValueError(f"Sprint with ID {sprint_id} not found")
        
        # Get team members
        members = self.member_repo.get_by_team(sprint.team_id)
        total_capacity = sum(member.capacity for member in members)
        
        # Get tasks
        tasks = self.task_repo.get_by_sprint(sprint_id)
        total_story_points = sum(task.story_points or 0 for task in tasks)
        
        # Estimate hours needed (rough calculation: 1 story point = ~8 hours)
        hours_needed = total_story_points * 8
        
        # Calculate utilization
        utilized = min(hours_needed, total_capacity * 5)  # 5 days sprint
        available = total_capacity * 5 - utilized
        utilization_pct = (utilized / (total_capacity * 5)) * 100 if total_capacity > 0 else 0
        
        return {
            "sprint_id": sprint_id,
            "total_capacity": total_capacity,
            "utilized_capacity": utilized,
            "available_capacity": available,
            "utilization_percentage": utilization_pct,
            "team_members": len(members),
            "total_tasks": len(tasks)
        }
    
    def record_resource_metrics(self, metrics_in: ResourceMetricsCreate) -> ResourceMetrics:
        """Record resource metrics for a sprint"""
        sprint = self.sprint_repo.get_by_id(metrics_in.sprint_id)
        if not sprint:
            raise ValueError(f"Sprint with ID {metrics_in.sprint_id} not found")
        
        return self.metrics_repo.create(metrics_in)
    
    def get_sprint_metrics_history(self, sprint_id: int) -> List[ResourceMetrics]:
        """Get historical metrics for a sprint"""
        return self.metrics_repo.get_by_sprint(sprint_id)
