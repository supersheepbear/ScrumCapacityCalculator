"""Scrum Capacity Calculator.

A web application to calculate Scrum team capacity and identify overloaded members
by comparing available working hours against planned work from Jira.
"""

__version__ = "1.0.0"

from scrum_capacity_calculator.core.calculator import CapacityCalculator
from scrum_capacity_calculator.core.calendar_service import CalendarService
from scrum_capacity_calculator.core.jira_parser import JiraParser
from scrum_capacity_calculator.models import (
    CapacityResult,
    JiraTask,
    Location,
    PTOEntry,
    Sprint,
    TeamMember,
    TeamSummary,
)

__all__ = [
    "CapacityCalculator",
    "CalendarService",
    "JiraParser",
    "CapacityResult",
    "JiraTask",
    "Location",
    "PTOEntry",
    "Sprint",
    "TeamMember",
    "TeamSummary",
]
