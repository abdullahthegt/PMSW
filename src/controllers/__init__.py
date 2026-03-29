"""
Controllers/Routes
FastAPI routes for API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from src.config import get_db
from src.services import (
    TeamService, SprintService, TaskService,
    TeamMemberService, ResourceAnalysisService
)
from src.schemas import (
    Team, TeamCreate, Sprint, SprintCreate,
    Task, TaskCreate, TeamMember, TeamMemberCreate
)

# Create routers
teams_router = APIRouter(prefix="/api/teams", tags=["Teams"])
sprints_router = APIRouter(prefix="/api/sprints", tags=["Sprints"])
tasks_router = APIRouter(prefix="/api/tasks", tags=["Tasks"])
members_router = APIRouter(prefix="/api/members", tags=["Team Members"])
resources_router = APIRouter(prefix="/api/resources", tags=["Resources"])


# ==================== TEAM ENDPOINTS ====================

@teams_router.post("/", response_model=Team, status_code=status.HTTP_201_CREATED)
def create_team(team_in: TeamCreate, db: Session = Depends(get_db)):
    """Create a new team"""
    try:
        service = TeamService(db)
        return service.create_team(team_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@teams_router.get("/{team_id}", response_model=Team)
def get_team(team_id: int, db: Session = Depends(get_db)):
    """Get a team by ID"""
    try:
        service = TeamService(db)
        return service.get_team(team_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@teams_router.get("/", response_model=List[Team])
def get_all_teams(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all teams"""
    service = TeamService(db)
    return service.get_all_teams(skip=skip, limit=limit)


@teams_router.put("/{team_id}", response_model=Team)
def update_team(team_id: int, team_in: TeamCreate, db: Session = Depends(get_db)):
    """Update a team"""
    try:
        service = TeamService(db)
        return service.update_team(team_id, team_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@teams_router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team(team_id: int, db: Session = Depends(get_db)):
    """Delete a team"""
    try:
        service = TeamService(db)
        service.delete_team(team_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ==================== SPRINT ENDPOINTS ====================

@sprints_router.post("/", response_model=Sprint, status_code=status.HTTP_201_CREATED)
def create_sprint(sprint_in: SprintCreate, db: Session = Depends(get_db)):
    """Create a new sprint"""
    try:
        service = SprintService(db)
        return service.create_sprint(sprint_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@sprints_router.get("/{sprint_id}", response_model=Sprint)
def get_sprint(sprint_id: int, db: Session = Depends(get_db)):
    """Get a sprint by ID"""
    try:
        service = SprintService(db)
        return service.get_sprint(sprint_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@sprints_router.get("/team/{team_id}", response_model=List[Sprint])
def get_team_sprints(team_id: int, db: Session = Depends(get_db)):
    """Get all sprints for a team"""
    try:
        service = SprintService(db)
        return service.get_team_sprints(team_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@sprints_router.get("/{sprint_id}/active", response_model=Sprint)
def get_active_sprint(sprint_id: int, db: Session = Depends(get_db)):
    """Get active sprint for a team"""
    service = SprintService(db)
    sprint = service.get_active_sprint(sprint_id)
    if not sprint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active sprint found")
    return sprint


@sprints_router.put("/{sprint_id}", response_model=Sprint)
def update_sprint(sprint_id: int, sprint_in: SprintCreate, db: Session = Depends(get_db)):
    """Update a sprint"""
    try:
        service = SprintService(db)
        return service.update_sprint(sprint_id, sprint_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@sprints_router.delete("/{sprint_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sprint(sprint_id: int, db: Session = Depends(get_db)):
    """Delete a sprint"""
    try:
        service = SprintService(db)
        service.delete_sprint(sprint_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ==================== TASK ENDPOINTS ====================

@tasks_router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(task_in: TaskCreate, db: Session = Depends(get_db)):
    """Create a new task"""
    try:
        service = TaskService(db)
        return service.create_task(task_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@tasks_router.get("/{task_id}", response_model=Task)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """Get a task by ID"""
    try:
        service = TaskService(db)
        return service.get_task(task_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@tasks_router.get("/sprint/{sprint_id}", response_model=List[Task])
def get_sprint_tasks(sprint_id: int, db: Session = Depends(get_db)):
    """Get all tasks in a sprint"""
    try:
        service = TaskService(db)
        return service.get_sprint_tasks(sprint_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@tasks_router.put("/{task_id}", response_model=Task)
def update_task(task_id: int, task_in: TaskCreate, db: Session = Depends(get_db)):
    """Update a task"""
    try:
        service = TaskService(db)
        return service.update_task(task_id, task_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@tasks_router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Delete a task"""
    try:
        service = TaskService(db)
        service.delete_task(task_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ==================== TEAM MEMBER ENDPOINTS ====================

@members_router.post("/", response_model=TeamMember, status_code=status.HTTP_201_CREATED)
def add_team_member(member_in: TeamMemberCreate, db: Session = Depends(get_db)):
    """Add a team member"""
    try:
        service = TeamMemberService(db)
        return service.add_team_member(member_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@members_router.get("/{member_id}", response_model=TeamMember)
def get_team_member(member_id: int, db: Session = Depends(get_db)):
    """Get a team member by ID"""
    try:
        service = TeamMemberService(db)
        return service.get_team_member(member_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@members_router.get("/team/{team_id}", response_model=List[TeamMember])
def get_team_members(team_id: int, db: Session = Depends(get_db)):
    """Get all members of a team"""
    try:
        service = TeamMemberService(db)
        return service.get_team_members(team_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@members_router.put("/{member_id}", response_model=TeamMember)
def update_team_member(member_id: int, member_in: TeamMemberCreate, db: Session = Depends(get_db)):
    """Update a team member"""
    try:
        service = TeamMemberService(db)
        return service.update_team_member(member_id, member_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@members_router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_team_member(member_id: int, db: Session = Depends(get_db)):
    """Remove a team member"""
    try:
        service = TeamMemberService(db)
        service.remove_team_member(member_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ==================== RESOURCE ANALYSIS ENDPOINTS ====================

@resources_router.get("/analysis/{sprint_id}")
def analyze_sprint_resources(sprint_id: int, db: Session = Depends(get_db)):
    """Analyze resource utilization for a sprint"""
    try:
        service = ResourceAnalysisService(db)
        return service.analyze_sprint_resources(sprint_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@resources_router.get("/history/{sprint_id}")
def get_metrics_history(sprint_id: int, db: Session = Depends(get_db)):
    """Get historical metrics for a sprint"""
    try:
        service = ResourceAnalysisService(db)
        return service.get_sprint_metrics_history(sprint_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
