"""
Database Models
ORM models for all database entities
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from src.config import Base


class Team(Base):
    """Team model"""
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sprints = relationship("Sprint", back_populates="team")
    team_members = relationship("TeamMember", back_populates="team")
    
    def __repr__(self):
        return f"<Team(id={self.id}, name={self.name})>"


class Sprint(Base):
    """Sprint model"""
    __tablename__ = "sprints"
    
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    planned_velocity = Column(Float, nullable=True)
    actual_velocity = Column(Float, nullable=True)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    team = relationship("Team", back_populates="sprints")
    tasks = relationship("Task", back_populates="sprint")
    
    def __repr__(self):
        return f"<Sprint(id={self.id}, name={self.name}, team_id={self.team_id})>"


class Task(Base):
    """Task model"""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    sprint_id = Column(Integer, ForeignKey("sprints.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    story_points = Column(Float, nullable=True)
    status = Column(String(50), default="todo")  # todo, in_progress, done
    assigned_to = Column(Integer, ForeignKey("team_members.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sprint = relationship("Sprint", back_populates="tasks")
    
    def __repr__(self):
        return f"<Task(id={self.id}, title={self.title}, sprint_id={self.sprint_id})>"


class TeamMember(Base):
    """Team Member model"""
    __tablename__ = "team_members"
    
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True)
    role = Column(String(100), nullable=True)
    capacity = Column(Float, default=8.0)  # hours per day
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    team = relationship("Team", back_populates="team_members")
    
    def __repr__(self):
        return f"<TeamMember(id={self.id}, name={self.name}, team_id={self.team_id})>"


class ResourceMetrics(Base):
    """Resource Metrics model"""
    __tablename__ = "resource_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    sprint_id = Column(Integer, ForeignKey("sprints.id"), nullable=False, index=True)
    total_capacity = Column(Float, nullable=False)
    utilized_capacity = Column(Float, nullable=False)
    available_capacity = Column(Float, nullable=False)
    utilization_percentage = Column(Float, nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<ResourceMetrics(sprint_id={self.sprint_id}, utilization={self.utilization_percentage}%)>"
