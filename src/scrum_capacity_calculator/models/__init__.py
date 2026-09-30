"""Data models for Scrum Capacity Calculator."""

from dataclasses import dataclass
from datetime import date
from typing import Optional
import math


@dataclass
class TeamMember:
    """Represents a team member with their work configuration."""

    name: str
    daily_hours: float
    location: str
    jira_name: Optional[str] = None
    group: str = "Team"

    def __post_init__(self):
        """Validate member data."""
        if not math.isfinite(self.daily_hours) or self.daily_hours <= 0 or self.daily_hours > 24:
            raise ValueError(f"daily_hours must be between 0 and 24, got {self.daily_hours}")
        if not self.name or not self.name.strip():
            raise ValueError("name cannot be empty")
        if not self.location or not self.location.strip():
            raise ValueError("location cannot be empty")
        if not self.group or not self.group.strip():
            raise ValueError("group cannot be empty")

        # Default jira_name to name if not provided
        if self.jira_name is None:
            self.jira_name = self.name

    def get_jira_name(self) -> str:
        """Get the name used for matching with Jira assignees."""
        return self.jira_name or self.name


@dataclass
class Sprint:
    """Represents a Sprint time period."""

    sprint_name: str
    start_date: date
    end_date: date

    def __post_init__(self):
        """Validate sprint data."""
        if not self.sprint_name or not self.sprint_name.strip():
            raise ValueError("sprint_name cannot be empty")
        if self.end_date <= self.start_date:
            raise ValueError(
                f"end_date ({self.end_date}) must be after start_date ({self.start_date})"
            )


    @property
    def duration_days(self) -> int:
        """Get sprint duration in calendar days (inclusive)."""
        return (self.end_date - self.start_date).days + 1


@dataclass
class PTOEntry:
    """Represents a personal time off entry."""

    name: str
    date: date
    hours: float

    def __post_init__(self):
        """Validate PTO data."""
        if not self.name or not self.name.strip():
            raise ValueError("name cannot be empty")
        if not math.isfinite(self.hours) or self.hours <= 0:
            raise ValueError(f"hours must be positive, got {self.hours}")


@dataclass
class Location:
    """Represents an office location with holiday configuration."""

    name: str
    country_code: str
    manual_holidays: list[date]

    def __post_init__(self):
        """Validate location data."""
        if not self.name or not self.name.strip():
            raise ValueError("name cannot be empty")
        if not self.country_code or not self.country_code.strip():
            raise ValueError("country_code cannot be empty")
        if self.manual_holidays is None:
            self.manual_holidays = []


@dataclass
class JiraTask:
    """Represents a task from Jira."""

    issue_key: str
    summary: str
    assignee: Optional[str]
    sprint: str
    estimate: float

    def __post_init__(self):
        """Validate task data."""
        if not self.issue_key or not self.issue_key.strip():
            raise ValueError("issue_key cannot be empty")
        if not math.isfinite(self.estimate) or self.estimate < 0:
            raise ValueError(f"estimate cannot be negative, got {self.estimate}")


@dataclass
class CapacityResult:
    """Represents capacity calculation result for a team member."""

    member_name: str
    location: str
    capacity_hours: float
    planned_hours: float
    remaining_hours: float
    load_rate: Optional[float]

    @property
    def status(self) -> str:
        """Get load status indicator."""
        if self.remaining_hours < 0:
            return "overload"
        elif self.load_rate is not None and self.load_rate >= 0.8:
            return "warning"
        else:
            return "normal"

@dataclass
class TeamSummary:
    """Represents team-wide capacity summary."""

    total_capacity: float
    total_planned: float
    total_remaining: float
    average_load_rate: float
    overloaded_count: int
    total_members: int
