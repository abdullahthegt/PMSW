"""
Resource Load Analyzer Module
Implements heuristic-based resource allocation with skill matching and bottleneck detection.
Solves the Multi-Mode Resource-Constrained Project Scheduling Problem (MRCPSP).
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import matplotlib.pyplot as plt
import seaborn as sns


class TeamMember:
    """Represents a team member with capacity and skills"""
    
    def __init__(self, member_id: int, name: str, role: str, skills: List[str],
                 availability_hours: int, efficiency: float):
        self.id = member_id
        self.name = name
        self.role = role
        self.skills = skills
        self.total_capacity = availability_hours
        self.remaining_capacity = availability_hours
        self.efficiency = efficiency
        self.assigned_tasks = []
        self.load_percent = 0.0

    def can_handle_task(self, required_skills: List[str]) -> bool:
        """Check if member has required skills"""
        return any(skill in self.skills for skill in required_skills)

    def assign_task(self, task_id: int, estimated_hours: float) -> bool:
        """Attempt to assign task"""
        actual_hours = estimated_hours / self.efficiency
        
        if actual_hours <= self.remaining_capacity:
            self.assigned_tasks.append({
                "task_id": task_id,
                "estimated_hours": estimated_hours,
                "actual_hours": actual_hours,
            })
            self.remaining_capacity -= actual_hours
            self.load_percent = (1 - self.remaining_capacity / self.total_capacity) * 100
            return True
        return False

    def get_status(self) -> str:
        """Get load status"""
        load = (self.total_capacity - self.remaining_capacity) / self.total_capacity
        
        if load > 1.0:
            return "Overloaded"
        elif load > 0.85:
            return "At Capacity"
        elif load > 0.65:
            return "Warning"
        else:
            return "Available"


class Task:
    """Represents a task/user story"""
    
    def __init__(self, task_id: int, title: str, task_type: str, asil: str,
                 story_points: int, estimated_hours: float, required_skills: List[str],
                 priority: int = 50, predecessors: List[int] = None):
        self.id = task_id
        self.title = title
        self.task_type = task_type
        self.asil = asil
        self.story_points = story_points
        self.estimated_hours = estimated_hours
        self.required_skills = required_skills
        self.priority = priority
        self.predecessors = predecessors or []
        self.assigned_to = None
        self.is_assigned = False
        self.feasible = True
        self.bottleneck_reason = None

    def get_priority_score(self) -> float:
        """Calculate priority score for allocation heuristic"""
        # Higher ASIL = higher priority
        asil_priority = {"QM": 1, "A": 2, "B": 3, "C": 4, "D": 5}
        asil_weight = asil_priority.get(self.asil, 3)
        
        # Weighted Shortest Job First (WSJF): value/effort
        wsjf_score = (asil_weight * self.story_points) / max(1, self.estimated_hours)
        
        return wsjf_score + (self.priority / 100)


class ResourceLoadAnalyzer:
    """
    Analyzes and optimizes resource allocation.
    Implements heuristic-based scheduling (greedy best-fit).
    """

    def __init__(self, team_df: pd.DataFrame, tasks_df: pd.DataFrame):
        """
        Initialize with team and task data.
        
        Args:
            team_df: DataFrame with columns [ID, Name, Role, Skills, Availability_Hours, Efficiency]
            tasks_df: DataFrame with columns [TaskID, Title, Type, ASIL, EstimatedHours, ...]
        """
        self.team = self._initialize_team(team_df)
        self.tasks = self._initialize_tasks(tasks_df)
        self.allocation_result = None
        self.bottleneck_analysis = None

    def _initialize_team(self, team_df: pd.DataFrame) -> List[TeamMember]:
        """Convert team DataFrame to TeamMember objects"""
        team = []
        
        for _, row in team_df.iterrows():
            skills = row["Skills"].split(";") if isinstance(row["Skills"], str) else []
            member = TeamMember(
                member_id=row["ID"],
                name=row["Name"],
                role=row["Role"],
                skills=[s.strip() for s in skills],
                availability_hours=int(row["Availability_Hours"]),
                efficiency=float(row["Efficiency"]),
            )
            team.append(member)
        
        return team

    def _initialize_tasks(self, tasks_df: pd.DataFrame) -> List[Task]:
        """Convert tasks DataFrame to Task objects"""
        tasks = []
        
        for _, row in tasks_df.iterrows():
            # Determine required skills based on task type
            required_skills = self._get_required_skills(
                row["Type"],
                row.get("ASPICE_Level", ""),
                row.get("ASIL", "QM")
            )
            
            task = Task(
                task_id=row["TaskID"],
                title=row["Title"],
                task_type=row["Type"],
                asil=row.get("ASIL", "QM"),
                story_points=row.get("StoryPoints", 5),
                estimated_hours=float(row["EstimatedHours"]),
                required_skills=required_skills,
                priority=50,  # Default priority
            )
            tasks.append(task)
        
        return tasks

    @staticmethod
    def _get_required_skills(task_type: str, aspice_level: str, asil: str) -> List[str]:
        """Map task type and ASPICE level to required skills"""
        skills = []
        
        # Task type skills
        type_skills = {
            "Requirement": ["Requirements", "Functional Safety"],
            "Design": ["Architecture", "System Design"],
            "Code": ["C/C++", "Embedded Systems", "AUTOSAR"],
            "Test": ["Unit Test", "HIL", "Test Automation"],
            "Safety Analysis": ["Functional Safety", "FMEA"],
            "Integration": ["Integration", "HIL"],
        }
        
        skills.extend(type_skills.get(task_type, []))
        
        # ASPICE level skills
        aspice_skills = {
            "SWE.1": ["Requirements"],
            "SWE.2": ["System Design"],
            "SWE.3": ["Architecture"],
            "SWE.4": ["Unit Test"],
            "SWE.5": ["Integration", "HIL"],
            "SWE.6": ["Test Automation"],
        }
        
        skills.extend(aspice_skills.get(aspice_level, []))
        
        # ASIL safety skills
        if asil in ["C", "D"]:
            skills.append("Functional Safety")
        
        return list(set(skills))  # Remove duplicates

    def _get_task_status(self, task: 'Task') -> str:
        """
        Determine task status based on assignment and constraints.
        
        Returns status string: Assigned, Overloaded, Delayed, Unassigned, Cancelled
        """
        if not task.is_assigned:
            if task.bottleneck_reason == "No team member with required skills":
                return "Cancelled"  # Skill gap - can't proceed
            elif task.bottleneck_reason:
                return "Delayed"  # Dependency or constraint - may proceed later
            else:
                return "Unassigned"  # Not yet assigned
        
        # Check if assigned member is overloaded
        assigned_member = next((m for m in self.team if m.name == task.assigned_to), None)
        if assigned_member and assigned_member.remaining_capacity < 0:
            return "Overloaded"
        
        return "Assigned"

    def _get_task_color(self, status: str) -> str:
        """Map task status to color code"""
        colors = {
            "Assigned": "#C8E6C9",     # Green
            "Overloaded": "#FFE0B2",   # Orange
            "Delayed": "#FFF9C4",      # Yellow
            "Unassigned": "#FFCDD2",   # Light red
            "Cancelled": "#BDBDBD",    # Gray
        }
        return colors.get(status, "#FFFFFF")

    def allocate_resources(self) -> Dict:
        """
        Allocate tasks to team members using greedy heuristic.
        
        Returns:
            Dict with allocation results, feasibility, and bottleneck analysis
        """
        # Reset team capacity
        for member in self.team:
            member.remaining_capacity = member.total_capacity
            member.assigned_tasks = []

        # Sort tasks by priority (Weighted Shortest Job First)
        sorted_tasks = sorted(self.tasks, key=lambda t: t.get_priority_score(), reverse=True)

        allocation_details = []
        infeasible_tasks = []

        for task in sorted_tasks:
            # Find capable team members
            candidates = [m for m in self.team if m.can_handle_task(task.required_skills)]

            if not candidates:
                task.feasible = False
                task.bottleneck_reason = "No team member with required skills"
                infeasible_tasks.append(task)
                continue

            # Sort candidates by remaining capacity (best-fit)
            candidates.sort(key=lambda m: m.remaining_capacity, reverse=True)

            assigned = False
            for candidate in candidates:
                if candidate.assign_task(task.id, task.estimated_hours):
                    task.assigned_to = candidate.name
                    task.is_assigned = True
                    assigned = True
                    break

            if not assigned:
                task.feasible = False
                task.bottleneck_reason = "Insufficient capacity in qualified team members"
                infeasible_tasks.append(task)
                
                # Try to assign anyway and flag as overload
                best_fit = min(candidates, key=lambda m: abs(m.remaining_capacity - task.estimated_hours))
                best_fit.assign_task(task.id, task.estimated_hours)
                task.assigned_to = best_fit.name

        # Compute final statuses for all tasks
        for task in self.tasks:
            final_status = self._get_task_status(task)
            
            allocated_to = task.assigned_to or "Unassigned"
            if final_status == "Overloaded":
                allocated_to = allocated_to.replace(" (OVERLOAD)", "") + " (OVERLOAD)"
            
            allocation_details.append({
                "TaskID": task.id,
                "Title": task.title,
                "AssignedTo": allocated_to,
                "EstimatedHours": round(task.estimated_hours, 1),
                "ActualHours": round(task.estimated_hours / (
                    next((m.efficiency for m in self.team if m.name == task.assigned_to), 1)
                ), 1) if task.assigned_to else 0,
                "Status": final_status,
                "Reason": task.bottleneck_reason or "",
            })

        # Analyze bottlenecks
        bottleneck_analysis = self._analyze_bottlenecks(infeasible_tasks)

        self.allocation_result = {
            "allocation_df": pd.DataFrame(allocation_details),
            "infeasible_tasks": infeasible_tasks,
            "bottleneck_analysis": bottleneck_analysis,
            "team_status": self._get_team_status(),
        }

        return self.allocation_result

    def _analyze_bottlenecks(self, infeasible_tasks: List[Task]) -> Dict:
        """Identify resource bottlenecks and constraints"""
        bottlenecks = {
            "skill_gaps": {},
            "overloaded_members": [],
            "critical_resources": [],
        }

        # Skill gaps
        all_required_skills = set()
        for task in self.tasks:
            all_required_skills.update(task.required_skills)

        for skill in all_required_skills:
            capable_members = [m for m in self.team if skill in m.skills]
            if len(capable_members) <= 1:
                bottlenecks["skill_gaps"][skill] = len(capable_members)
                bottlenecks["critical_resources"].extend(capable_members)

        # Overloaded members
        for member in self.team:
            if member.remaining_capacity < 0:
                bottlenecks["overloaded_members"].append({
                    "name": member.name,
                    "role": member.role,
                    "overload_hours": abs(member.remaining_capacity),
                    "load_percent": member.load_percent,
                })

        return bottlenecks

    def _get_team_status(self) -> pd.DataFrame:
        """Get load status of each team member"""
        status_rows = []
        
        for member in self.team:
            status_rows.append({
                "Name": member.name,
                "Role": member.role,
                "Capacity": member.total_capacity,
                "Used": round(member.total_capacity - member.remaining_capacity, 1),
                "Remaining": round(member.remaining_capacity, 1),
                "LoadPercent": round(member.load_percent, 1),
                "Status": member.get_status(),
                "TaskCount": len(member.assigned_tasks),
            })
        
        return pd.DataFrame(status_rows)

    def get_allocation_summary(self) -> Dict:
        """Get high-level allocation summary"""
        if self.allocation_result is None:
            raise ValueError("Must call allocate_resources() first")

        total_tasks = len(self.tasks)
        assigned_tasks = sum(1 for t in self.tasks if t.is_assigned)
        feasible_tasks = sum(1 for t in self.tasks if t.feasible)

        total_capacity = sum(m.total_capacity for m in self.team)
        total_used = sum(m.total_capacity - m.remaining_capacity for m in self.team)

        return {
            "total_tasks": total_tasks,
            "assigned_tasks": assigned_tasks,
            "assignment_rate": round((assigned_tasks / total_tasks) * 100, 1),
            "total_team_capacity": total_capacity,
            "total_load": round(total_used, 1),
            "capacity_utilization": round((total_used / total_capacity) * 100, 1),
        }

    def generate_load_heatmap(self, figsize: Tuple = (14, 6)) -> plt.Figure:
        """
        Generate modern heatmap of team member load.

        Returns:
            matplotlib figure object
        """
        if self.allocation_result is None:
            raise ValueError("Must call allocate_resources() first")

        # Create data matrix: team members vs load status
        team_names = [m.name for m in self.team]
        load_percents = [m.load_percent for m in self.team]
        statuses = [m.get_status() for m in self.team]

        # Modern color palette
        fig, ax = plt.subplots(figsize=figsize, facecolor='white')

        # Create modern color mapping
        def get_status_color(status):
            colors = {
                "Available": "#4CAF50",      # Modern green
                "Warning": "#FF9800",       # Modern orange
                "At Capacity": "#F57C00",   # Modern deep orange
                "Overloaded": "#D32F2F"     # Modern red
            }
            return colors.get(status, "#9E9E9E")

        colors = [get_status_color(status) for status in statuses]

        # Create horizontal bars with modern styling
        bars = ax.barh(team_names, load_percents, color=colors,
                      height=0.6, edgecolor='white', linewidth=1, alpha=0.9)

        # Add modern value labels
        for i, (bar, percent, status) in enumerate(zip(bars, load_percents, statuses)):
            # Background box for text
            ax.text(percent + 1, bar.get_y() + bar.get_height() / 2,
                   f"{percent:.0f}%", va="center", fontsize=10,
                   fontweight="bold", color="white",
                   bbox=dict(boxstyle="round,pad=0.3", facecolor=get_status_color(status),
                           edgecolor='none', alpha=0.9))

        # Add modern reference lines with subtle styling
        reference_lines = [
            (65, "#FFEB3B", "Warning Zone (65%)", ":"),
            (85, "#FF9800", "Capacity Limit (85%)", "-"),
            (100, "#F44336", "Overload (100%)", "-")
        ]

        for threshold, color, label, style in reference_lines:
            ax.axvline(x=threshold, color=color, linestyle=style,
                      linewidth=1.5, alpha=0.6, label=label)

        # Modern axis styling
        ax.set_xlabel("Workload Utilization (%)", fontsize=12, fontweight="medium",
                     color="#424242", labelpad=10)
        ax.set_title("Team Workload Distribution", fontsize=16, fontweight="bold",
                    color="#212121", pad=20)

        # Set limits with some padding
        max_load = max(load_percents) if load_percents else 100
        ax.set_xlim(0, max(110, max_load + 15))

        # Modern legend
        ax.legend(loc="lower right", fontsize=9, framealpha=0.95,
                 edgecolor='none', labelspacing=0.5, handlelength=2)

        # Subtle grid
        ax.grid(True, axis="x", alpha=0.2, linestyle='-', color='#E0E0E0')
        ax.set_axisbelow(True)

        # Clean axis styling
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#BDBDBD')
        ax.spines['bottom'].set_color('#BDBDBD')

        # Clean ticks
        ax.tick_params(axis='both', which='major', labelsize=10, colors='#616161')

        # Tight layout
        plt.tight_layout()

        return fig

    def generate_skill_coverage_chart(self, figsize: Tuple = (12, 8)) -> plt.Figure:
        """
        Generate modern skill coverage heatmap showing which team members have which skills.

        Returns:
            matplotlib figure object
        """
        if self.allocation_result is None:
            raise ValueError("Must call allocate_resources() first")

        # Collect all unique skills
        all_skills = set()
        for member in self.team:
            all_skills.update(member.skills)
        all_skills = sorted(list(all_skills))

        # Create skill coverage matrix (presence/absence)
        team_names = [m.name for m in self.team]
        skill_matrix = []

        for member in self.team:
            member_skills = []
            for skill in all_skills:
                has_skill = 1 if skill in member.skills else 0
                member_skills.append(has_skill)
            skill_matrix.append(member_skills)

        # Modern heatmap styling
        fig, ax = plt.subplots(figsize=figsize, facecolor='white')

        # Create heatmap with modern color scheme (binary: has skill or not)
        cmap = plt.cm.Greens  # Green colormap for presence
        im = ax.imshow(skill_matrix, cmap=cmap, aspect='auto', alpha=0.9, vmin=0, vmax=1)

        # Add skill presence annotations
        for i in range(len(team_names)):
            for j in range(len(all_skills)):
                has_skill = skill_matrix[i][j]
                if has_skill == 1:
                    ax.text(j, i, "✓", ha="center", va="center",
                           fontsize=12, fontweight="bold", color="white")

        # Modern axis styling
        ax.set_xticks(range(len(all_skills)))
        ax.set_yticks(range(len(team_names)))
        ax.set_xticklabels(all_skills, rotation=45, ha="right", fontsize=10,
                          fontweight="medium", color="#424242")
        ax.set_yticklabels(team_names, fontsize=10, fontweight="medium", color="#424242")

        # Modern title and labels
        ax.set_title("Team Skill Coverage Matrix", fontsize=16, fontweight="bold",
                    color="#212121", pad=20)
        ax.set_xlabel("Skills", fontsize=12, fontweight="medium", color="#424242", labelpad=10)
        ax.set_ylabel("Team Members", fontsize=12, fontweight="medium", color="#424242", labelpad=10)

        # Add colorbar with modern styling
        cbar = plt.colorbar(im, ax=ax, shrink=0.8, aspect=20, pad=0.02)
        cbar.set_label("Skill Coverage", fontsize=11, fontweight="medium", color="#424242", labelpad=10)
        cbar.set_ticks([0, 1])
        cbar.set_ticklabels(["Not Available", "Available"])
        cbar.ax.tick_params(labelsize=9, colors="#616161")

        # Clean axis styling
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#BDBDBD')
        ax.spines['bottom'].set_color('#BDBDBD')

        # Add subtle grid
        ax.set_xticks([x - 0.5 for x in range(1, len(all_skills))], minor=True)
        ax.set_yticks([y - 0.5 for y in range(1, len(team_names))], minor=True)
        ax.grid(which="minor", color="#E0E0E0", linestyle='-', linewidth=0.5, alpha=0.3)
        ax.tick_params(which="minor", bottom=False, left=False)

        # Tight layout
        plt.tight_layout()

        return fig

    def generate_asil_distribution_chart(self, figsize: Tuple = (10, 6)) -> plt.Figure:
        """
        Generate visualization of ASIL (safety criticality) distribution across tasks.

        Returns:
            matplotlib figure object
        """
        asil_dist = self.get_asil_distribution()
        
        # Sort by safety criticality (D is highest)
        asil_order = ["D", "C", "B", "A", "QM"]
        asil_dist_sorted = {asil: asil_dist[asil] for asil in asil_order if asil in asil_dist}
        
        # Modern color scheme (darker = more critical)
        colors = {
            "D": "#B71C1C",      # Dark red (highest criticality)
            "C": "#D32F2F",      # Red
            "B": "#FF9800",      # Orange
            "A": "#FBC02D",      # Amber
            "QM": "#4CAF50"      # Green (no safety requirement)
        }
        
        fig, ax = plt.subplots(figsize=figsize, facecolor='white')
        
        asils = list(asil_dist_sorted.keys())
        hours = [asil_dist_sorted[asil]["hours"] for asil in asils]
        bar_colors = [colors[asil] for asil in asils]
        
        bars = ax.bar(asils, hours, color=bar_colors, edgecolor='white', linewidth=2, alpha=0.9)
        
        # Add value labels and percentage
        for bar, asil in zip(bars, asils):
            height = bar.get_height()
            pct = asil_dist_sorted[asil]["percentage"]
            ax.text(bar.get_x() + bar.get_width() / 2, height,
                   f"{height:.0f}h\n({pct:.1f}%)",
                   ha="center", va="bottom", fontsize=11, fontweight="bold")
        
        # ASIL descriptions
        asil_desc = {
            "D": "Highest Safety\nCriticality",
            "C": "High Safety\nCriticality",
            "B": "Medium Safety\nCriticality",
            "A": "Low Safety\nCriticality",
            "QM": "No Safety\nRequirement"
        }
        
        ax.set_xticklabels([f"{asil}\n{asil_desc[asil]}" for asil in asils], 
                          fontsize=10, fontweight="medium", color="#424242")
        ax.set_ylabel("Estimated Hours", fontsize=12, fontweight="medium", color="#424242")
        ax.set_title("Safety-Criticality (ASIL) Distribution", fontsize=16, fontweight="bold", 
                    color="#212121", pad=20)
        
        # Clean styling
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#BDBDBD')
        ax.spines['bottom'].set_color('#BDBDBD')
        ax.grid(True, axis="y", alpha=0.2, linestyle='-', color='#E0E0E0')
        ax.set_axisbelow(True)
        ax.tick_params(axis='both', which='major', labelsize=10, colors='#616161')
        
        plt.tight_layout()
        
        return fig

    def generate_asil_distribution_chart(self, figsize: Tuple = (10, 6)) -> plt.Figure:
        """
        Generate visualization of ASIL (safety criticality) distribution across tasks.

        Returns:
            matplotlib figure object
        """
        asil_dist = self.get_asil_distribution()
        
        # Sort by safety criticality (D is highest)
        asil_order = ["D", "C", "B", "A", "QM"]
        asil_dist_sorted = {asil: asil_dist[asil] for asil in asil_order if asil in asil_dist}
        
        # Modern color scheme (darker = more critical)
        colors = {
            "D": "#B71C1C",      # Dark red (highest criticality)
            "C": "#D32F2F",      # Red
            "B": "#FF9800",      # Orange
            "A": "#FBC02D",      # Amber
            "QM": "#4CAF50"      # Green (no safety requirement)
        }
        
        fig, ax = plt.subplots(figsize=figsize, facecolor='white')
        
        asils = list(asil_dist_sorted.keys())
        hours = [asil_dist_sorted[asil]["hours"] for asil in asils]
        bar_colors = [colors[asil] for asil in asils]
        
        bars = ax.bar(asils, hours, color=bar_colors, edgecolor='white', linewidth=2, alpha=0.9)
        
        # Add value labels and percentage
        for bar, asil in zip(bars, asils):
            height = bar.get_height()
            pct = asil_dist_sorted[asil]["percentage"]
            ax.text(bar.get_x() + bar.get_width() / 2, height,
                   f"{height:.0f}h\n({pct:.1f}%)",
                   ha="center", va="bottom", fontsize=11, fontweight="bold")
        
        # ASIL descriptions
        asil_desc = {
            "D": "Highest Safety\nCriticality",
            "C": "High Safety\nCriticality",
            "B": "Medium Safety\nCriticality",
            "A": "Low Safety\nCriticality",
            "QM": "No Safety\nRequirement"
        }
        
        ax.set_xticklabels([f"{asil}\n{asil_desc[asil]}" for asil in asils], 
                          fontsize=10, fontweight="medium", color="#424242")
        ax.set_ylabel("Estimated Hours", fontsize=12, fontweight="medium", color="#424242")
        ax.set_title("Safety-Criticality (ASIL) Distribution", fontsize=16, fontweight="bold", 
                    color="#212121", pad=20)
        
        # Clean styling
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#BDBDBD')
        ax.spines['bottom'].set_color('#BDBDBD')
        ax.grid(True, axis="y", alpha=0.2, linestyle='-', color='#E0E0E0')
        ax.set_axisbelow(True)
        ax.tick_params(axis='both', which='major', labelsize=10, colors='#616161')
        
        plt.tight_layout()
        
        return fig

    def get_asil_distribution(self) -> Dict:
        """
        Analyze ASIL (Automotive Safety Integrity Level) distribution.
        Returns breakdown by safety criticality level.
        """
        asil_counts = {}
        asil_hours = {}
        total_hours = 0
        
        for task in self.tasks:
            asil = task.asil
            asil_counts[asil] = asil_counts.get(asil, 0) + 1
            asil_hours[asil] = asil_hours.get(asil, 0) + task.estimated_hours
            total_hours += task.estimated_hours
        
        # Calculate percentages
        asil_distribution = {}
        asil_priority = {"D": 5, "C": 4, "B": 3, "A": 2, "QM": 1}
        
        for asil in sorted(asil_counts.keys(), key=lambda x: asil_priority.get(x, 0), reverse=True):
            count = asil_counts[asil]
            hours = asil_hours[asil]
            pct = (hours / total_hours * 100) if total_hours > 0 else 0
            
            asil_distribution[asil] = {
                "count": count,
                "hours": round(hours, 1),
                "percentage": round(pct, 1),
            }
        
        return asil_distribution

    def get_safety_critical_bottlenecks(self) -> List[str]:
        """
        Identify bottlenecks specifically affecting safety-critical tasks (ASIL C, D).
        Returns list of critical safety concerns.
        """
        if self.allocation_result is None:
            return []
        
        safety_alerts = []
        
        # Find safety-critical unassigned tasks
        critical_tasks = [t for t in self.allocation_result["infeasible_tasks"] 
                         if t.asil in ["C", "D"]]
        
        if critical_tasks:
            critical_count = len(critical_tasks)
            safety_alerts.append(
                f"🚨 CRITICAL SAFETY RISK: {critical_count} ASIL-C/D task(s) cannot be scheduled. "
                f"Safety compliance may be impacted."
            )
        
        # Check for overloaded team members handling safety-critical work
        for member in self.team:
            critical_assigned = [t for t in self.tasks 
                               if t.assigned_to == member.name and t.asil in ["C", "D"]]
            if critical_assigned and member.remaining_capacity < 0:
                safety_alerts.append(
                    f"⚠️ SAFETY CONCERN: {member.name} is overloaded with ASIL-C/D task(s). "
                    f"Quality risk for safety-critical features."
                )
        
        # Check skill coverage for safety-critical tasks
        safety_critical_skills = set()
        for task in self.tasks:
            if task.asil in ["C", "D"]:
                safety_critical_skills.update(task.required_skills)
        
        for skill in safety_critical_skills:
            capable = [m for m in self.team if skill in m.skills]
            if len(capable) == 1:
                safety_alerts.append(
                    f"⚠️ SINGLE POINT OF FAILURE: Only {capable[0].name} has '{skill}' "
                    f"(needed for ASIL-C/D tasks). Recommend cross-training."
                )
        
        return safety_alerts

    def suggest_rebalancing(self) -> List[str]:

        """
        Suggest rebalancing actions to resolve bottlenecks.
        Prioritizes safety-critical tasks (ASIL C, D).
        
        Returns:
            List of actionable recommendations ordered by safety priority
        """
        suggestions = []

        if self.allocation_result is None:
            return ["Must call allocate_resources() first"]

        # Priority 1: Safety-critical bottlenecks
        safety_alerts = self.get_safety_critical_bottlenecks()
        suggestions.extend(safety_alerts)

        # Priority 2: Overload suggestions (prioritize safety tasks)
        overloaded = self.allocation_result["bottleneck_analysis"]["overloaded_members"]
        for overload in overloaded:
            # Check if overloaded member has safety-critical tasks
            member_tasks = [t for t in self.tasks if t.assigned_to == overload['name']]
            critical_tasks = [t for t in member_tasks if t.asil in ["C", "D"]]
            
            if critical_tasks:
                suggestions.append(
                    f"🚨 {overload['name']} is overloaded by {overload['overload_hours']:.1f}h "
                    f"INCLUDING ASIL-C/D tasks. URGENT: Reassign safety tasks or add capacity immediately."
                )
            else:
                suggestions.append(
                    f"⚠ {overload['name']} is overloaded by {overload['overload_hours']:.1f} hours. "
                    f"Consider reassigning tasks or adding capacity."
                )

        # Priority 3: Skill gap suggestions (note safety-critical skills)
        skill_gaps = self.allocation_result["bottleneck_analysis"]["skill_gaps"]
        for skill, count in skill_gaps.items():
            # Check if this skill is needed for ASIL-C/D tasks
            critical_need = any(
                skill in t.required_skills and t.asil in ["C", "D"] 
                for t in self.tasks
            )
            
            if count == 0:
                if critical_need:
                    suggestions.append(
                        f"🚨 CRITICAL SKILL GAP: NO TEAM MEMBER has '{skill}' (needed for ASIL-C/D tasks). "
                        f"Hire safety specialist immediately."
                    )
                else:
                    suggestions.append(
                        f"✗ NO TEAM MEMBER has skill '{skill}'. "
                        f"Hire specialist or train existing team member."
                    )
            elif count == 1:
                if critical_need:
                    suggestions.append(
                        f"⚠️ SAFETY RISK: Only 1 team member has '{skill}' for ASIL-C/D work. "
                        f"Single point of failure - cross-train backup immediately."
                    )
                else:
                    suggestions.append(
                        f"⚠ Only 1 team member has skill '{skill}'. "
                        f"Single point of failure - consider cross-training."
                    )

        # Priority 4: Infeasible tasks (with safety context)
        if self.allocation_result["infeasible_tasks"]:
            critical_infeasible = [t for t in self.allocation_result["infeasible_tasks"] 
                                  if t.asil in ["C", "D"]]
            other_infeasible = [t for t in self.allocation_result["infeasible_tasks"] 
                               if t.asil not in ["C", "D"]]
            
            if critical_infeasible:
                suggestions.append(
                    f"🚨 {len(critical_infeasible)} ASIL-C/D task(s) cannot be scheduled. "
                    f"Safety deadline at risk. Increase capacity or hire specialists immediately."
                )
            
            if other_infeasible:
                suggestions.append(
                    f"⚠ {len(other_infeasible)} task(s) could not be scheduled (non-critical). "
                    f"Reduce scope, increase capacity, or defer tasks."
                )

        if not suggestions:
            suggestions.append("✓ Resource allocation is feasible with no critical bottlenecks.")

        return suggestions


if __name__ == "__main__":
    # Example usage
    from synthetic_data_generator import SyntheticDataGenerator
    
    generator = SyntheticDataGenerator(seed=42)
    dataset = generator.generate_complete_project_dataset()
    
    analyzer = ResourceLoadAnalyzer(dataset["team"], dataset["backlog"])
    result = analyzer.allocate_resources()
    
    print("RESOURCE LOAD ANALYSIS")
    print("=" * 60)
    
    print("\nAllocation Summary:")
    summary = analyzer.get_allocation_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    print("\nTeam Status:")
    print(analyzer._get_team_status())
    
    print("\nRebalancing Suggestions:")
    for suggestion in analyzer.suggest_rebalancing():
        print(f"  {suggestion}")
