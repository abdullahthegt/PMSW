# Automotive DSS - Layered Architecture Documentation

## Architecture Overview

This project implements a **3-layer architecture** with a separation of concerns for better maintainability, testability, and scalability.

### Layer Structure

```
┌─────────────────────────────────────────────┐
│         Controller Layer (API)              │
│     - FastAPI routes and endpoints          │
└──────────────┬──────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│      Service Layer (Business Logic)         │
│     - Orchestrates repositories             │
│     - Business rules & validation           │
│     - Domain logic implementation           │
└──────────────┬──────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│     Repository Layer (Data Abstraction)     │
│     - Provides entity-specific queries      │
│     - Business-level data operations        │
└──────────────┬──────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│   Data Access Layer (Database Operations)   │
│     - Low-level database queries            │
│     - CRUD operations using SQLAlchemy      │
└──────────────┬──────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│           Database (SQLite/SQL)             │
│     - Data persistence                      │
└─────────────────────────────────────────────┘
```

## Directory Structure

```
src/
├── config/              # Database configuration
│   └── __init__.py      # SQLAlchemy setup, session management
├── models/              # Database models (ORM)
│   └── __init__.py      # SQLAlchemy ORM models
├── schemas/             # Pydantic schemas (API validation)
│   └── __init__.py      # Request/Response models
├── data_access/         # Data Access Layer
│   └── __init__.py      # Generic DataAccessLayer class
├── repositories/        # Repository Layer
│   └── __init__.py      # Entity-specific repositories
├── services/            # Service Layer (Business Logic)
│   └── __init__.py      # Business logic services
├── controllers/         # Controller Layer (API Routes)
│   └── __init__.py      # FastAPI routes and endpoints
└── utils/               # Utility functions
    └── __init__.py      # Helper functions
```

## Layer Descriptions

### 1. Data Access Layer (`data_access/`)
**Purpose**: Provides generic database operations

**Key Components**:
- `DataAccessLayer`: Generic class for CRUD operations
- Methods: `create()`, `read()`, `update()`, `delete()`, `filter()`, `filter_one()`

**Responsibility**: 
- Direct database queries using SQLAlchemy
- No business logic
- Reusable across all models

**Example**:
```python
dal = DataAccessLayer(db, Team)
team = dal.read(1)
teams = dal.filter(is_active=True)
```

### 2. Repository Layer (`repositories/`)
**Purpose**: Abstracts data access for specific entities

**Key Components**:
- `TeamRepository`: Team-specific operations
- `SprintRepository`: Sprint-specific operations
- `TaskRepository`: Task-specific operations
- `TeamMemberRepository`: Team member operations
- `ResourceMetricsRepository`: Metrics operations

**Responsibility**:
- Entity-specific queries and operations
- Business-level data operations
- Acts as a contract between services and data access
- Simplifies testing with mock repositories

**Example**:
```python
repo = TeamRepository(db)
team = repo.get_by_id(1)
team = repo.get_by_name("Development Team")
teams = repo.get_all()
```

### 3. Service Layer (`services/`)
**Purpose**: Implements business logic and orchestrates repositories

**Key Components**:
- `TeamService`: Team business logic
- `SprintService`: Sprint management
- `TaskService`: Task management and velocity calculation
- `TeamMemberService`: Team capacity management
- `ResourceAnalysisService`: Resource utilization analysis

**Responsibility**:
- Business rules and validation
- Orchestrates multiple repositories
- Error handling
- Complex business operations
- Data transformation

**Example**:
```python
service = TeamService(db)
team = service.create_team(team_in)  # Validates and creates
service.update_team(1, team_in)      # Business logic before update
velocity = service.calculate_sprint_velocity(sprint_id)
```

### 4. Controller Layer (`controllers/`)
**Purpose**: Handles HTTP requests/responses

**Key Components**:
- `teams_router`: Team endpoints
- `sprints_router`: Sprint endpoints
- `tasks_router`: Task endpoints
- `members_router`: Team member endpoints
- `resources_router`: Resource analysis endpoints

**Responsibility**:
- HTTP request handling
- Route definition
- Request validation (via Pydantic schemas)
- Response formatting
- HTTP status codes
- Error handling for HTTP

**Example**:
```python
@teams_router.get("/{team_id}", response_model=Team)
def get_team(team_id: int, db: Session = Depends(get_db)):
    service = TeamService(db)
    return service.get_team(team_id)
```

### 5. Models (`models/`)
**Purpose**: ORM models defining database schema

**Key Models**:
- `Team`: Teams that sprints belong to
- `Sprint`: Sprints with start/end dates
- `Task`: Tasks within sprints
- `TeamMember`: Team members with capacity
- `ResourceMetrics`: Historical resource utilization

### 6. Schemas (`schemas/`)
**Purpose**: Pydantic models for API validation

**Key Schemas**:
- `TeamCreate`: Request to create team
- `Team`: Response with team data
- `SprintCreate`: Request to create sprint
- `Sprint`: Response with sprint data
- Similar for Task, TeamMember, ResourceMetrics

## Data Flow

### Example: Creating a Team

```
1. HTTP Request (POST /api/teams)
         ↓
2. Controller Layer
   - Validates request via Pydantic schema
   - Extracts data from request
         ↓
3. Service Layer
   - Checks if team name already exists
   - Applies business rules
   - Calls repository method
         ↓
4. Repository Layer
   - Prepares data for database
   - Calls data access layer
         ↓
5. Data Access Layer
   - Creates SQLAlchemy model instance
   - Commits to database
         ↓
6. Response
   - Returns created Team object
   - Serializes to JSON via Pydantic
         ↓
7. HTTP Response (201 Created)
```

## Benefits of This Architecture

### 1. **Separation of Concerns**
- Each layer has a specific responsibility
- Changes to one layer don't affect others

### 2. **Testability**
- Easy to mock repositories
- Can test services independently
- Controllers can be tested with mock services

### 3. **Reusability**
- Repositories can be used by multiple services
- Data access layer is generic and reusable

### 4. **Maintainability**
- Clear structure makes code easier to navigate
- Easier to locate and fix bugs
- Reduces code duplication

### 5. **Scalability**
- Easy to add new entities with same pattern
- Can introduce caching at repository layer
- Database changes isolated to data access layer

### 6. **Flexibility**
- Can switch database without changing services
- Can create multiple implementations of repositories
- Easy to add new business logic

## Running the Application

### Development API Server
```bash
# Install dependencies
pip install -r requirements.txt

# Run FastAPI server
python -m uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

Visit `http://localhost:8000/docs` for interactive API documentation.

### Original Streamlit Dashboard
```bash
streamlit run app.py
```

## Key Endpoints

### Teams
- `POST /api/teams` - Create team
- `GET /api/teams/{team_id}` - Get team
- `GET /api/teams` - List all teams
- `PUT /api/teams/{team_id}` - Update team
- `DELETE /api/teams/{team_id}` - Delete team

### Sprints
- `POST /api/sprints` - Create sprint
- `GET /api/sprints/{sprint_id}` - Get sprint
- `GET /api/sprints/team/{team_id}` - Get team sprints
- `PUT /api/sprints/{sprint_id}` - Update sprint
- `DELETE /api/sprints/{sprint_id}` - Delete sprint

### Tasks
- `POST /api/tasks` - Create task
- `GET /api/tasks/{task_id}` - Get task
- `GET /api/tasks/sprint/{sprint_id}` - Get sprint tasks
- `PUT /api/tasks/{task_id}` - Update task
- `DELETE /api/tasks/{task_id}` - Delete task

### Team Members
- `POST /api/members` - Add member
- `GET /api/members/{member_id}` - Get member
- `GET /api/members/team/{team_id}` - Get team members
- `PUT /api/members/{member_id}` - Update member
- `DELETE /api/members/{member_id}` - Remove member

### Resource Analysis
- `GET /api/resources/analysis/{sprint_id}` - Analyze sprint resources
- `GET /api/resources/history/{sprint_id}` - Get metrics history

## Next Steps: React Frontend

The React frontend will:
1. Call the FastAPI backend endpoints
2. Display teams, sprints, and tasks
3. Show resource utilization charts
4. Manage team members and sprints
5. Analyze velocity and capacity trends

The layered backend is now ready to support the React frontend!
