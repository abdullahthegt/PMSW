"""
Utility functions and helpers
"""

from datetime import datetime, timedelta
from typing import List


def calculate_sprint_duration_days(start_date: datetime, end_date: datetime) -> int:
    """Calculate the number of days in a sprint"""
    return (end_date - start_date).days


def is_sprint_active(start_date: datetime, end_date: datetime) -> bool:
    """Check if a sprint is currently active"""
    now = datetime.utcnow()
    return start_date <= now <= end_date


def get_days_remaining(end_date: datetime) -> int:
    """Get number of days remaining in a sprint"""
    now = datetime.utcnow()
    if end_date > now:
        return (end_date - now).days
    return 0


def calculate_velocity_trend(velocities: List[float]) -> str:
    """Analyze velocity trend (improving, declining, stable)"""
    if len(velocities) < 2:
        return "insufficient_data"
    
    recent = velocities[-3:] if len(velocities) >= 3 else velocities
    older = velocities[:-3] if len(velocities) >= 3 else velocities[:-1]
    
    recent_avg = sum(recent) / len(recent)
    older_avg = sum(older) / len(older) if older else recent_avg
    
    change = recent_avg - older_avg
    
    if change > 0:
        return "improving"
    elif change < 0:
        return "declining"
    else:
        return "stable"
