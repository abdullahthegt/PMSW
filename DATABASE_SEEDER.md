# Database Management Commands

## Overview

This project includes easy-to-use commands for managing your database. You can seed the database with 100+ fake records or reset it to a fresh state.

## 📊 Quick Stats

After running `python seeder.py seed`, your database will contain:
- **3 Teams** (Backend, Frontend, DevOps)
- **15 Team Members** (5 per team with different roles)
- **9 Sprints** (3 per team, 2-week duration)
- **72 Tasks** (8 per sprint with story points)
- **45 Resource Metrics** (historical utilization snapshots)

**Total: 144+ Records** of realistic fake data

---

## 🚀 Commands

### 1. **Seed Database with Fake Data**

```bash
python seeder.py seed
```

**What it does:**
- Resets current data (if any)
- Creates 3 teams with realistic descriptions
- Adds 15 team members with names, emails, roles, and capacity
- Creates 9 sprints with start/end dates, planned and actual velocity
- Creates 72 tasks with titles, descriptions, story points, and assignments
- Creates 45 resource utilization metrics with historical data

**Example Output:**
```
================================================================================
🌱 DATABASE SEEDING STARTED
================================================================================

👥 Seeding 3 teams...
✅ Created 3 teams

👨‍💼 Seeding team members...
✅ Created 15 team members

🏃 Seeding sprints...
✅ Created 9 sprints

📝 Seeding tasks...
✅ Created 72 tasks

📊 Seeding resource metrics...
✅ Created 45 resource metrics

================================================================================
✅ DATABASE SEEDING COMPLETED SUCCESSFULLY
================================================================================
```

---

### 2. **Reset Database to Fresh State**

```bash
python seeder.py reset
```

**What it does:**
- Deletes ALL tables and data
- Recreates empty table structure
- Confirms before proceeding with warning

**Safety Feature:**
The command requires confirmation:
```
🗑️  WARNING: This will delete ALL data from the database. Continue? (yes/no): 
```

---

### 3. **Inspect Database Schema**

```bash
python inspect_db.py
```

**What it shows:**
- Database file location and size
- All table names
- Column names and data types
- Primary keys and foreign keys
- Row counts for each table
- Sample data (first 5 rows of each table)

**Example Output:**
```
📁 Database File Information:
  Location: C:\Users\...\automotive_dss.db
  Size: 84.00 KB

📊 TABLE: TEAMS
  Columns (5):
    • id (INTEGER, NOT NULL)
    • name (VARCHAR(255), NOT NULL)
    • description (TEXT, NULL)
    • created_at (DATETIME, NULL)
    • updated_at (DATETIME, NULL)
  Row Count: 3
```

---

### 4. **View Specific Table Data**

Using `manage.py` (Alternative CLI):

```bash
python manage.py view teams
python manage.py view tasks
python manage.py view sprints
```

Shows up to 20 rows from the specified table.

---

## 🛠️ Using `manage.py` - Master CLI Tool

For easier management, use the `manage.py` script:

```bash
# Seed the database
python manage.py seed

# Reset the database
python manage.py reset

# Inspect entire database
python manage.py inspect

# View specific table
python manage.py view teams
python manage.py view tasks
python manage.py view sprints
python manage.py view team_members
python manage.py view resource_metrics

# Show help
python manage.py help
```

---

## 📋 Database Tables Explained

### TEAMS
Container for organizing team members and sprints

**Fields:**
- `id` - Unique identifier
- `name` - Team name (Backend Team, Frontend Team, etc.)
- `description` - Team description
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp

### TEAM_MEMBERS
Individual team members with their capacity and roles

**Fields:**
- `id` - Unique identifier
- `team_id` - Foreign key to TEAMS
- `name` - Member name
- `email` - Email address
- `role` - Job role (Developer, QA Engineer, Team Lead, etc.)
- `capacity` - Hours available per day (6-9 hours)
- `is_active` - Whether member is active
- `created_at`, `updated_at` - Timestamps

### SPRINTS
2-week work iterations for each team

**Fields:**
- `id` - Unique identifier
- `team_id` - Foreign key to TEAMS
- `name` - Sprint name
- `start_date` - Sprint start date
- `end_date` - Sprint end date (14 days later)
- `planned_velocity` - Expected story points
- `actual_velocity` - Achieved story points
- `is_active` - Whether sprint is currently active
- `created_at`, `updated_at` - Timestamps

### TASKS
Individual work items assigned to sprints

**Fields:**
- `id` - Unique identifier
- `sprint_id` - Foreign key to SPRINTS
- `title` - Task description
- `description` - Detailed description
- `story_points` - Effort estimate (1, 2, 3, 5, 8, 13)
- `status` - Task status (todo, in_progress, done)
- `assigned_to` - Foreign key to TEAM_MEMBERS
- `created_at`, `updated_at` - Timestamps

### RESOURCE_METRICS
Historical snapshots of resource utilization

**Fields:**
- `id` - Unique identifier
- `sprint_id` - Foreign key to SPRINTS
- `total_capacity` - Total team hours available
- `utilized_capacity` - Hours actually used
- `available_capacity` - Hours remaining
- `utilization_percentage` - % of capacity used
- `recorded_at` - When this snapshot was taken

---

## 🔄 Workflow Example

### Initial Setup:
```bash
# 1. First time - seed with data
python seeder.py seed

# 2. Inspect what was created
python inspect_db.py

# 3. Start the API server
python -m uvicorn api:app --reload
```

### During Development:
```bash
# View teams
python manage.py view teams

# Check current data
python inspect_db.py

# Test API at http://localhost:8000/docs
```

### Need Fresh Start:
```bash
# Reset database
python seeder.py reset

# Reseed with fresh fake data
python seeder.py seed
```

---

## 🌐 Accessing Data via API

All seeded data is accessible via REST endpoints:

```bash
# Get all teams
curl http://localhost:8000/api/teams

# Get specific team
curl http://localhost:8000/api/teams/1

# Get team sprints
curl http://localhost:8000/api/sprints/team/1

# Get sprint tasks
curl http://localhost:8000/api/tasks/sprint/1

# Analyze sprint resources
curl http://localhost:8000/api/resources/analysis/1
```

**Interactive API Documentation:**
Open `http://localhost:8000/docs` for Swagger UI to test all endpoints!

---

## 🗄️ Database File Location

```
C:\Users\92335\Desktop\Automotive Managment tool\automotive-dss\automotive_dss.db
```

This SQLite file contains all your data and can be opened with:
- **DB Browser for SQLite** (Recommended GUI tool)
- **SQLite command line**
- **Any SQLite editor**

---

## ⚙️ Advanced Usage

### Customize Seed Data

Edit `seeder.py` to change:
- Number of teams: `seed_teams(count=3)`
- Team members per team: `seed_team_members(teams, members_per_team=5)`
- Sprints per team: `seed_sprints(teams, sprints_per_team=3)`
- Tasks per sprint: `seed_tasks(sprints, tasks_per_sprint=8)`

### Custom Data Script

Create your own seeding script:

```python
from seeder import DatabaseSeeder

seeder = DatabaseSeeder()
teams = seeder.seed_teams(count=5)
seeder.seed_team_members(teams, members_per_team=10)
# ... etc
```

---

## 🐛 Troubleshooting

**Q: "ModuleNotFoundError: No module named 'faker'"**
```bash
python -m pip install faker
```

**Q: "Database is locked"**
- Close any other tools accessing the database
- Restart your API server

**Q: "Want to start over?"**
```bash
python seeder.py reset
python seeder.py seed
```

---

## Summary

| Command | Purpose |
|---------|---------|
| `python seeder.py seed` | Populate database with 144+ fake records |
| `python seeder.py reset` | Delete all data and reset to empty |
| `python inspect_db.py` | View complete database schema and stats |
| `python manage.py view <table>` | View specific table data |
| `python manage.py help` | Show available commands |

**Your database is now fully set up and seeded with realistic test data!** 🎉
