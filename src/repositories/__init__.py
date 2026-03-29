"""
Repository Layer
Provides abstraction over data access for specific domain entities
"""

from sqlalchemy.orm import Session
from typing import Optional, List
from src.data_access import DataAccessLayer
from src.models import Team, Sprint, Task, TeamMember, ResourceMetrics
from src.schemas import (
    TeamCreate, SprintCreate, TaskCreate, 
    TeamMemberCreate, ResourceMetricsCreate
)


class BaseRepository:
    """Base repository with common operations"""
    
    def __init__(self, db: Session):
        self.db = db


class TeamRepository(BaseRepository):
    """Repository for Team operations"""
    
    def create(self, team_in: TeamCreate) -> Team:
        """Create a new team"""
        dal = DataAccessLayer(self.db, Team)
        return dal.create(team_in)
    
    def get_by_id(self, team_id: int) -> Optional[Team]:
        """Get team by ID"""
        dal = DataAccessLayer(self.db, Team)
        return dal.read(team_id)
    
    def get_by_name(self, name: str) -> Optional[Team]:
        """Get team by name"""
        dal = DataAccessLayer(self.db, Team)
        return dal.filter_one(name=name)
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Team]:
        """Get all teams"""
        dal = DataAccessLayer(self.db, Team)
        return dal.read_all(skip=skip, limit=limit)
    
    def update(self, team_id: int, team_in: TeamCreate) -> Optional[Team]:
        """Update a team"""
        dal = DataAccessLayer(self.db, Team)
        return dal.update(team_id, team_in)
    
    def delete(self, team_id: int) -> bool:
        """Delete a team"""
        dal = DataAccessLayer(self.db, Team)
        return dal.delete(team_id)


class SprintRepository(BaseRepository):
    """Repository for Sprint operations"""
    
    def create(self, sprint_in: SprintCreate) -> Sprint:
        """Create a new sprint"""
        dal = DataAccessLayer(self.db, Sprint)
        return dal.create(sprint_in)
    
    def get_by_id(self, sprint_id: int) -> Optional[Sprint]:
        """Get sprint by ID"""
        dal = DataAccessLayer(self.db, Sprint)
        return dal.read(sprint_id)
    
    def get_by_team(self, team_id: int) -> List[Sprint]:
        """Get all sprints for a team"""
        dal = DataAccessLayer(self.db, Sprint)
        return dal.filter(team_id=team_id)
    
    def get_active_sprint(self, team_id: int) -> Optional[Sprint]:
        """Get active sprint for a team"""
        dal = DataAccessLayer(self.db, Sprint)
        sprints = dal.filter(team_id=team_id, is_active=True)
        return sprints[0] if sprints else None
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Sprint]:
        """Get all sprints"""
        dal = DataAccessLayer(self.db, Sprint)
        return dal.read_all(skip=skip, limit=limit)
    
    def update(self, sprint_id: int, sprint_in: SprintCreate) -> Optional[Sprint]:
        """Update a sprint"""
        dal = DataAccessLayer(self.db, Sprint)
        return dal.update(sprint_id, sprint_in)
    
    def delete(self, sprint_id: int) -> bool:
        """Delete a sprint"""
        dal = DataAccessLayer(self.db, Sprint)
        return dal.delete(sprint_id)


class TaskRepository(BaseRepository):
    """Repository for Task operations"""
    
    def create(self, task_in: TaskCreate) -> Task:
        """Create a new task"""
        dal = DataAccessLayer(self.db, Task)
        return dal.create(task_in)
    
    def get_by_id(self, task_id: int) -> Optional[Task]:
        """Get task by ID"""
        dal = DataAccessLayer(self.db, Task)
        return dal.read(task_id)
    
    def get_by_sprint(self, sprint_id: int) -> List[Task]:
        """Get all tasks in a sprint"""
        dal = DataAccessLayer(self.db, Task)
        return dal.filter(sprint_id=sprint_id)
    
    def get_by_status(self, sprint_id: int, status: str) -> List[Task]:
        """Get tasks by status in a sprint"""
        dal = DataAccessLayer(self.db, Task)
        return dal.filter(sprint_id=sprint_id, status=status)
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Task]:
        """Get all tasks"""
        dal = DataAccessLayer(self.db, Task)
        return dal.read_all(skip=skip, limit=limit)
    
    def update(self, task_id: int, task_in: TaskCreate) -> Optional[Task]:
        """Update a task"""
        dal = DataAccessLayer(self.db, Task)
        return dal.update(task_id, task_in)
    
    def delete(self, task_id: int) -> bool:
        """Delete a task"""
        dal = DataAccessLayer(self.db, Task)
        return dal.delete(task_id)


class TeamMemberRepository(BaseRepository):
    """Repository for TeamMember operations"""
    
    def create(self, member_in: TeamMemberCreate) -> TeamMember:
        """Create a new team member"""
        dal = DataAccessLayer(self.db, TeamMember)
        return dal.create(member_in)
    
    def get_by_id(self, member_id: int) -> Optional[TeamMember]:
        """Get team member by ID"""
        dal = DataAccessLayer(self.db, TeamMember)
        return dal.read(member_id)
    
    def get_by_team(self, team_id: int) -> List[TeamMember]:
        """Get all members of a team"""
        dal = DataAccessLayer(self.db, TeamMember)
        return dal.filter(team_id=team_id, is_active=True)
    
    def get_by_email(self, email: str) -> Optional[TeamMember]:
        """Get team member by email"""
        dal = DataAccessLayer(self.db, TeamMember)
        return dal.filter_one(email=email)
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[TeamMember]:
        """Get all team members"""
        dal = DataAccessLayer(self.db, TeamMember)
        return dal.read_all(skip=skip, limit=limit)
    
    def update(self, member_id: int, member_in: TeamMemberCreate) -> Optional[TeamMember]:
        """Update a team member"""
        dal = DataAccessLayer(self.db, TeamMember)
        return dal.update(member_id, member_in)
    
    def delete(self, member_id: int) -> bool:
        """Delete a team member"""
        dal = DataAccessLayer(self.db, TeamMember)
        return dal.delete(member_id)


class ResourceMetricsRepository(BaseRepository):
    """Repository for ResourceMetrics operations"""
    
    def create(self, metrics_in: ResourceMetricsCreate) -> ResourceMetrics:
        """Create new resource metrics"""
        dal = DataAccessLayer(self.db, ResourceMetrics)
        return dal.create(metrics_in)
    
    def get_by_sprint(self, sprint_id: int) -> List[ResourceMetrics]:
        """Get all metrics for a sprint"""
        dal = DataAccessLayer(self.db, ResourceMetrics)
        return dal.filter(sprint_id=sprint_id)
    
    def get_latest_by_sprint(self, sprint_id: int) -> Optional[ResourceMetrics]:
        """Get latest metrics for a sprint"""
        dal = DataAccessLayer(self.db, ResourceMetrics)
        metrics = dal.filter(sprint_id=sprint_id)
        return sorted(metrics, key=lambda x: x.recorded_at, reverse=True)[0] if metrics else None
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[ResourceMetrics]:
        """Get all resource metrics"""
        dal = DataAccessLayer(self.db, ResourceMetrics)
        return dal.read_all(skip=skip, limit=limit)
