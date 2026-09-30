"""Core capacity calculator."""

from datetime import date
from typing import List, Dict, Set
from collections import defaultdict

from scrum_capacity_calculator.models import (
    TeamMember, Sprint, PTOEntry, Location, JiraTask,
    CapacityResult, TeamSummary
)
from scrum_capacity_calculator.core.calendar_service import CalendarService


class CapacityCalculator:
    """Calculates team capacity and compares with planned work."""

    def __init__(self, calendar_service: CalendarService = None):
        """
        Initialize calculator.

        Args:
            calendar_service: Calendar service for working day calculations.
                            If None, creates default instance.
        """
        self.calendar_service = calendar_service or CalendarService()

    def calculate_member_capacity(
        self,
        member: TeamMember,
        sprint: Sprint,
        location: Location,
        ptos: List[PTOEntry]
    ) -> float:
        """
        Calculate available capacity for a team member.

        Args:
            member: Team member
            sprint: Sprint period
            location: Member's office location
            ptos: List of all PTO entries (will filter by member)

        Returns:
            Available capacity in hours
        """
        # Get holidays for location
        years = {sprint.start_date.year, sprint.end_date.year}
        all_holidays = set()
        for year in years:
            holidays = self.calendar_service.get_holidays_for_location(
                location.country_code,
                year,
                location.manual_holidays
            )
            all_holidays.update(holidays)

        # Filter holidays to sprint date range
        sprint_holidays = {
            h for h in all_holidays
            if sprint.start_date <= h <= sprint.end_date
        }

        # Get member's PTO dates and hours
        member_ptos = [p for p in ptos if p.name == member.name]
        pto_dates = set()
        partial_pto_hours = 0.0

        for pto in member_ptos:
            if sprint.start_date <= pto.date <= sprint.end_date:
                if pto.hours >= member.daily_hours:
                    # Full day PTO
                    pto_dates.add(pto.date)
                else:
                    # Partial day PTO - handle separately
                    partial_pto_hours += pto.hours

        # Calculate working days
        working_days = self.calendar_service.get_working_days(
            sprint.start_date,
            sprint.end_date,
            sprint_holidays,
            pto_dates
        )

        # Convert to hours and subtract partial PTO
        capacity_hours = (working_days * member.daily_hours) - partial_pto_hours

        return max(0, capacity_hours)  # Never negative

    def calculate_planned_work(
        self,
        member: TeamMember,
        sprint: Sprint,
        tasks: List[JiraTask]
    ) -> float:
        """
        Calculate planned work for a team member in a sprint.

        Args:
            member: Team member
            sprint: Sprint period
            tasks: All Jira tasks

        Returns:
            Total planned hours
        """
        jira_name = member.get_jira_name()

        planned_hours = sum(
            task.estimate
            for task in tasks
            if task.assignee == jira_name and task.sprint == sprint.sprint_name
        )

        return planned_hours

    def calculate_capacity_results(
        self,
        members: List[TeamMember],
        sprint: Sprint,
        locations: List[Location],
        ptos: List[PTOEntry],
        tasks: List[JiraTask]
    ) -> List[CapacityResult]:
        """
        Calculate capacity results for all team members.

        Args:
            members: List of team members
            sprint: Sprint period
            locations: List of office locations
            ptos: List of PTO entries
            tasks: List of Jira tasks

        Returns:
            List of capacity results, sorted by load rate descending
        """
        # Build location lookup
        location_map = {loc.name: loc for loc in locations}

        results = []
        for member in members:
            location = location_map.get(member.location)
            if not location:
                raise ValueError(f"Location '{member.location}' not found for member '{member.name}'")

            capacity = self.calculate_member_capacity(member, sprint, location, ptos)
            planned = self.calculate_planned_work(member, sprint, tasks)
            remaining = capacity - planned
            load_rate = planned / capacity if capacity > 0 else 0

            result = CapacityResult(
                member_name=member.name,
                location=member.location,
                capacity_hours=capacity,
                planned_hours=planned,
                remaining_hours=remaining,
                load_rate=load_rate
            )
            results.append(result)

        # Sort by load rate descending (overloaded first)
        results.sort(key=lambda r: r.load_rate, reverse=True)

        return results

    def calculate_team_summary(
        self,
        results: List[CapacityResult]
    ) -> TeamSummary:
        """
        Calculate team-wide summary.

        Args:
            results: Individual capacity results

        Returns:
            Team summary
        """
        if not results:
            return TeamSummary(
                total_capacity=0,
                total_planned=0,
                total_remaining=0,
                average_load_rate=0,
                overloaded_count=0,
                total_members=0
            )

        total_capacity = sum(r.capacity_hours for r in results)
        total_planned = sum(r.planned_hours for r in results)
        total_remaining = total_capacity - total_planned
        average_load_rate = total_planned / total_capacity if total_capacity > 0 else 0
        overloaded_count = sum(1 for r in results if r.status == "overload")

        return TeamSummary(
            total_capacity=total_capacity,
            total_planned=total_planned,
            total_remaining=total_remaining,
            average_load_rate=average_load_rate,
            overloaded_count=overloaded_count,
            total_members=len(results)
        )

    def get_unassigned_tasks(
        self,
        sprint: Sprint,
        tasks: List[JiraTask]
    ) -> List[JiraTask]:
        """Get tasks with no assignee in the sprint."""
        return [
            task for task in tasks
            if task.sprint == sprint.sprint_name and not task.assignee
        ]

    def get_unestimated_tasks(
        self,
        sprint: Sprint,
        tasks: List[JiraTask]
    ) -> List[JiraTask]:
        """Get tasks with zero or missing estimate in the sprint."""
        return [
            task for task in tasks
            if task.sprint == sprint.sprint_name and task.estimate == 0
        ]

    def get_unmatched_assignees(
        self,
        members: List[TeamMember],
        sprint: Sprint,
        tasks: List[JiraTask]
    ) -> Dict[str, float]:
        """
        Get assignees in Jira that don't match any team member.

        Returns:
            Dict of {assignee_name: total_hours}
        """
        member_jira_names = {m.get_jira_name() for m in members}

        unmatched = defaultdict(float)
        for task in tasks:
            if task.sprint == sprint.sprint_name and task.assignee:
                if task.assignee not in member_jira_names:
                    unmatched[task.assignee] += task.estimate

        return dict(unmatched)
