"""
Database Seeder
Populates the database with fake data for testing and development
"""

from faker import Faker
from datetime import datetime, timedelta
import random
from sqlalchemy.orm import Session

from src.config import SessionLocal, engine, Base
from src.models import Team, Sprint, Task, TeamMember, ResourceMetrics


class DatabaseSeeder:
    """Seed the database with fake data"""
    
    def __init__(self):
        self.fake = Faker()
        self.db = SessionLocal()
    
    def reset_database(self):
        """Drop all tables and recreate them"""
        print("🗑️  Resetting database...")
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        print("✅ Database reset successfully")
    
    def seed_teams(self, count: int = 3):
        """Create fake teams"""
        print(f"\n👥 Seeding {count} teams...")
        
        team_names = [
            "Backend Team",
            "Frontend Team",
            "DevOps Team",
            "QA Team",
            "Mobile Team",
            "Data Team",
            "Security Team"
        ]
        
        teams = []
        for i in range(min(count, len(team_names))):
            team = Team(
                name=team_names[i],
                description=self.fake.sentence(nb_words=8),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            self.db.add(team)
            teams.append(team)
        
        self.db.commit()
        print(f"✅ Created {count} teams")
        return teams
    
    def seed_team_members(self, teams: list, members_per_team: int = 5):
        """Create fake team members"""
        print(f"\n👨‍💼 Seeding team members...")
        
        roles = ["Developer", "Senior Developer", "Team Lead", "QA Engineer", "Product Manager", "Designer"]
        
        total_created = 0
        for team in teams:
            for _ in range(members_per_team):
                member = TeamMember(
                    team_id=team.id,
                    name=self.fake.name(),
                    email=self.fake.email(),
                    role=random.choice(roles),
                    capacity=random.choice([6.0, 7.0, 8.0, 9.0]),  # hours per day
                    is_active=self.fake.boolean(chance_of_getting_true=90),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                self.db.add(member)
                total_created += 1
        
        self.db.commit()
        print(f"✅ Created {total_created} team members")
    
    def seed_sprints(self, teams: list, sprints_per_team: int = 3):
        """Create fake sprints"""
        print(f"\n🏃 Seeding sprints...")
        
        sprints = []
        total_created = 0
        
        for team in teams:
            # Create sprints with 2-week duration
            start_date = datetime.utcnow() - timedelta(days=60)
            
            for i in range(sprints_per_team):
                sprint_start = start_date + timedelta(days=14*i)
                sprint_end = sprint_start + timedelta(days=14)
                
                is_active = (sprint_start <= datetime.utcnow() <= sprint_end)
                
                sprint = Sprint(
                    team_id=team.id,
                    name=f"{team.name} - Sprint {i+1}",
                    start_date=sprint_start,
                    end_date=sprint_end,
                    planned_velocity=random.uniform(20, 50),
                    actual_velocity=random.uniform(15, 45) if not is_active else None,
                    is_active=is_active,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                self.db.add(sprint)
                sprints.append(sprint)
                total_created += 1
        
        self.db.commit()
        print(f"✅ Created {total_created} sprints")
        return sprints
    
    def seed_tasks(self, sprints: list, tasks_per_sprint: int = 8):
        """Create fake tasks"""
        print(f"\n📝 Seeding tasks...")
        
        statuses = ["todo", "in_progress", "done"]
        
        total_created = 0
        for sprint in sprints:
            # Get team members for assignment
            team_members = self.db.query(TeamMember).filter(
                TeamMember.team_id == sprint.team_id
            ).all()
            
            for _ in range(tasks_per_sprint):
                task = Task(
                    sprint_id=sprint.id,
                    title=self.fake.sentence(nb_words=6),
                    description=self.fake.paragraph(nb_sentences=3),
                    story_points=random.choice([1, 2, 3, 5, 8, 13]),
                    status=random.choice(statuses),
                    assigned_to=random.choice(team_members).id if team_members else None,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                self.db.add(task)
                total_created += 1
        
        self.db.commit()
        print(f"✅ Created {total_created} tasks")
    
    def seed_resource_metrics(self, sprints: list):
        """Create fake resource metrics"""
        print(f"\n📊 Seeding resource metrics...")
        
        total_created = 0
        for sprint in sprints:
            # Create 5 metric snapshots per sprint
            for day_offset in range(0, min((sprint.end_date - sprint.start_date).days, 10), 2):
                metric_date = sprint.start_date + timedelta(days=day_offset)
                
                # Get team members
                team_members = self.db.query(TeamMember).filter(
                    TeamMember.team_id == sprint.team_id,
                    TeamMember.is_active == True
                ).all()
                
                total_capacity = sum(m.capacity for m in team_members) * 5  # 5 days in sprint
                utilized = random.uniform(total_capacity * 0.5, total_capacity * 0.9)
                available = total_capacity - utilized
                utilization_pct = (utilized / total_capacity * 100) if total_capacity > 0 else 0
                
                metric = ResourceMetrics(
                    sprint_id=sprint.id,
                    total_capacity=total_capacity,
                    utilized_capacity=utilized,
                    available_capacity=available,
                    utilization_percentage=utilization_pct,
                    recorded_at=metric_date
                )
                self.db.add(metric)
                total_created += 1
        
        self.db.commit()
        print(f"✅ Created {total_created} resource metrics")
    
    def seed_all(self):
        """Seed all tables with fake data"""
        try:
            print("\n" + "="*80)
            print("🌱 DATABASE SEEDING STARTED")
            print("="*80)
            
            # Seed in order
            teams = self.seed_teams(count=3)
            self.seed_team_members(teams, members_per_team=5)
            sprints = self.seed_sprints(teams, sprints_per_team=3)
            self.seed_tasks(sprints, tasks_per_sprint=8)
            self.seed_resource_metrics(sprints)
            
            print("\n" + "="*80)
            print("✅ DATABASE SEEDING COMPLETED SUCCESSFULLY")
            print("="*80)
            print("\nSummary:")
            print(f"  • Teams: 3")
            print(f"  • Team Members: 15")
            print(f"  • Sprints: 9")
            print(f"  • Tasks: 72")
            print(f"  • Resource Metrics: ~27")
            print("\n")
            
        except Exception as e:
            print(f"\n❌ Error during seeding: {e}")
            self.db.rollback()
            raise
        finally:
            self.db.close()


def seed_database():
    """CLI command to seed the database"""
    seeder = DatabaseSeeder()
    seeder.seed_all()


def reset_database():
    """CLI command to reset the database"""
    confirm = input("⚠️  WARNING: This will delete ALL data from the database. Continue? (yes/no): ")
    if confirm.lower() == 'yes':
        seeder = DatabaseSeeder()
        seeder.reset_database()
        print("\n")
    else:
        print("Reset cancelled.\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python seeder.py [seed|reset]")
        print("\nCommands:")
        print("  seed   - Populate database with fake data")
        print("  reset  - Delete all data and reset database to fresh state")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "seed":
        seed_database()
    elif command == "reset":
        reset_database()
    else:
        print(f"Unknown command: {command}")
        print("Use 'seed' or 'reset'")
        sys.exit(1)
