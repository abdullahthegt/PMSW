"""
Data Schemas (Pydantic Models)
Used for API request/response validation
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class TeamBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class TeamCreate(TeamBase):
    pass


class Team(TeamBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SprintBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    start_date: datetime
    end_date: datetime
    planned_velocity: Optional[float] = None
    is_active: bool = False


class SprintCreate(SprintBase):
    team_id: int


class Sprint(SprintBase):
    id: int
    team_id: int
    actual_velocity: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    story_points: Optional[float] = None
    status: str = "todo"


class TaskCreate(TaskBase):
    sprint_id: int
    assigned_to: Optional[int] = None


class Task(TaskBase):
    id: int
    sprint_id: int
    assigned_to: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TeamMemberBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    role: Optional[str] = None
    capacity: float = 8.0


class TeamMemberCreate(TeamMemberBase):
    team_id: int


class TeamMember(TeamMemberBase):
    id: int
    team_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ResourceMetricsBase(BaseModel):
    total_capacity: float
    utilized_capacity: float
    available_capacity: float
    utilization_percentage: float


class ResourceMetricsCreate(ResourceMetricsBase):
    sprint_id: int


class ResourceMetrics(ResourceMetricsBase):
    id: int
    sprint_id: int
    recorded_at: datetime
    
    class Config:
        from_attributes = True
