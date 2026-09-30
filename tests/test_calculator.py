"""Tests for capacity calculator."""

import pytest
from datetime import date
from scrum_capacity_calculator.core.calculator import CapacityCalculator
from scrum_capacity_calculator.core.calendar_service import CalendarService
from scrum_capacity_calculator.models import (
    TeamMember, Sprint, PTOEntry, Location, JiraTask
)


class TestCapacityCalculator:
    """Test capacity calculator logic."""

    @pytest.fixture
    def calculator(self):
        """Create calculator instance."""
        return CapacityCalculator()

    @pytest.fixture
    def sprint(self):
        """Create test sprint."""
        return Sprint(
            sprint_name="2024-Q1-Sprint-1",
            start_date=date(2024, 1, 8),
            end_date=date(2024, 1, 19)
        )

    @pytest.fixture
    def location_beijing(self):
        """Create Beijing location."""
        return Location(
            name="Beijing",
            country_code="CN",
            manual_holidays=[]
        )

    @pytest.fixture
    def member_john(self):
        """Create test member John."""
        return TeamMember(
            name="John Doe",
            jira_name="john.doe",
            daily_hours=8,
            location="Beijing"
        )

    @pytest.fixture
    def member_jane(self):
        """Create test member Jane with part-time hours."""
        return TeamMember(
            name="Jane Smith",
            jira_name="jane.smith",
            daily_hours=6,
            location="Beijing"
        )

    def test_calculate_member_capacity_no_pto(
        self, calculator, member_john, sprint, location_beijing
    ):
        """Test capacity calculation with no PTO."""
        capacity = calculator.calculate_member_capacity(
            member_john,
            sprint,
            location_beijing,
            []
        )

        # 10 working days * 8 hours = 80 hours
        assert capacity == 80.0

    def test_calculate_member_capacity_with_full_day_pto(
        self, calculator, member_john, sprint, location_beijing
    ):
        """Test capacity calculation with full day PTO."""
        ptos = [
            PTOEntry(name="John Doe", date=date(2024, 1, 10), hours=8)
        ]

        capacity = calculator.calculate_member_capacity(
            member_john,
            sprint,
            location_beijing,
            ptos
        )

        # 9 working days * 8 hours = 72 hours
        assert capacity == 72.0

    def test_calculate_member_capacity_with_partial_pto(
        self, calculator, member_john, sprint, location_beijing
    ):
        """Test capacity calculation with partial day PTO."""
        ptos = [
            PTOEntry(name="John Doe", date=date(2024, 1, 10), hours=4)
        ]

        capacity = calculator.calculate_member_capacity(
            member_john,
            sprint,
            location_beijing,
            ptos
        )

        # 10 working days * 8 hours - 4 hours partial PTO = 76 hours
        assert capacity == 76.0

    def test_calculate_member_capacity_part_time(
        self, calculator, member_jane, sprint, location_beijing
    ):
        """Test capacity calculation for part-time member."""
        capacity = calculator.calculate_member_capacity(
            member_jane,
            sprint,
            location_beijing,
            []
        )

        # 10 working days * 6 hours = 60 hours
        assert capacity == 60.0

    def test_calculate_member_capacity_ignores_other_member_pto(
        self, calculator, member_john, sprint, location_beijing
    ):
        """Test that one member's PTO doesn't affect another."""
        ptos = [
            PTOEntry(name="Jane Smith", date=date(2024, 1, 10), hours=6)
        ]

        capacity = calculator.calculate_member_capacity(
            member_john,
            sprint,
            location_beijing,
            ptos
        )

        # Should be 80 hours (Jane's PTO doesn't affect John)
        assert capacity == 80.0

    def test_calculate_planned_work(self, calculator, member_john, sprint):
        """Test planned work calculation."""
        tasks = [
            JiraTask("PROJ-1", "Task 1", "john.doe", "2024-Q1-Sprint-1", 16),
            JiraTask("PROJ-2", "Task 2", "john.doe", "2024-Q1-Sprint-1", 24),
            JiraTask("PROJ-3", "Task 3", "jane.smith", "2024-Q1-Sprint-1", 12),
        ]

        planned = calculator.calculate_planned_work(member_john, sprint, tasks)

        assert planned == 40.0  # 16 + 24

    def test_calculate_planned_work_different_sprint(
        self, calculator, member_john, sprint
    ):
        """Test that tasks from other sprints are not counted."""
        tasks = [
            JiraTask("PROJ-1", "Task 1", "john.doe", "2024-Q1-Sprint-1", 16),
            JiraTask("PROJ-2", "Task 2", "john.doe", "2024-Q1-Sprint-2", 24),
        ]

        planned = calculator.calculate_planned_work(member_john, sprint, tasks)

        assert planned == 16.0  # Only Sprint-1 task

    def test_calculate_capacity_results(
        self, calculator, member_john, member_jane, sprint, location_beijing
    ):
        """Test calculating results for multiple members."""
        members = [member_john, member_jane]
        locations = [location_beijing]
        ptos = []
        tasks = [
            JiraTask("PROJ-1", "Task 1", "john.doe", "2024-Q1-Sprint-1", 88),
            JiraTask("PROJ-2", "Task 2", "jane.smith", "2024-Q1-Sprint-1", 48),
        ]

        results = calculator.calculate_capacity_results(
            members, sprint, locations, ptos, tasks
        )

        assert len(results) == 2

        # Should be sorted by load rate descending
        # John: 88/80 = 110% (overload)
        # Jane: 48/60 = 80% (warning)
        assert results[0].member_name == "John Doe"
        assert results[0].capacity_hours == 80.0
        assert results[0].planned_hours == 88.0
        assert results[0].remaining_hours == -8.0
        assert results[0].load_rate == 1.1
        assert results[0].status == "overload"

        assert results[1].member_name == "Jane Smith"
        assert results[1].capacity_hours == 60.0
        assert results[1].planned_hours == 48.0
        assert results[1].load_rate == 0.8
        assert results[1].status == "warning"

    def test_calculate_team_summary(self, calculator):
        """Test team summary calculation."""
        from scrum_capacity_calculator.models import CapacityResult

        results = [
            CapacityResult("John", "Beijing", 80, 88, -8, 1.1),
            CapacityResult("Jane", "Beijing", 60, 48, 12, 0.8),
            CapacityResult("Bob", "Shanghai", 80, 40, 40, 0.5),
        ]

        summary = calculator.calculate_team_summary(results)

        assert summary.total_capacity == 220.0
        assert summary.total_planned == 176.0
        assert summary.total_remaining == 44.0
        assert summary.average_load_rate == pytest.approx(0.8)
        assert summary.overloaded_count == 1
        assert summary.total_members == 3

    def test_get_unassigned_tasks(self, calculator, sprint):
        """Test getting unassigned tasks."""
        tasks = [
            JiraTask("PROJ-1", "Task 1", "john.doe", "2024-Q1-Sprint-1", 16),
            JiraTask("PROJ-2", "Task 2", None, "2024-Q1-Sprint-1", 24),
            JiraTask("PROJ-3", "Task 3", None, "2024-Q1-Sprint-1", 12),
        ]

        unassigned = calculator.get_unassigned_tasks(sprint, tasks)

        assert len(unassigned) == 2
        assert unassigned[0].issue_key == "PROJ-2"
        assert unassigned[1].issue_key == "PROJ-3"

    def test_get_unestimated_tasks(self, calculator, sprint):
        """Test getting unestimated tasks."""
        tasks = [
            JiraTask("PROJ-1", "Task 1", "john.doe", "2024-Q1-Sprint-1", 16),
            JiraTask("PROJ-2", "Task 2", "jane.smith", "2024-Q1-Sprint-1", 0),
            JiraTask("PROJ-3", "Task 3", "bob.lee", "2024-Q1-Sprint-1", 0),
        ]

        unestimated = calculator.get_unestimated_tasks(sprint, tasks)

        assert len(unestimated) == 2
        assert unestimated[0].issue_key == "PROJ-2"

    def test_get_unmatched_assignees(
        self, calculator, member_john, member_jane, sprint
    ):
        """Test getting assignees that don't match any team member."""
        members = [member_john, member_jane]
        tasks = [
            JiraTask("PROJ-1", "Task 1", "john.doe", "2024-Q1-Sprint-1", 16),
            JiraTask("PROJ-2", "Task 2", "external.contractor", "2024-Q1-Sprint-1", 24),
            JiraTask("PROJ-3", "Task 3", "external.contractor", "2024-Q1-Sprint-1", 16),
        ]

        unmatched = calculator.get_unmatched_assignees(members, sprint, tasks)

        assert len(unmatched) == 1
        assert "external.contractor" in unmatched
        assert unmatched["external.contractor"] == 40.0  # 24 + 16

    def test_capacity_never_negative(
        self, calculator, member_john, sprint, location_beijing
    ):
        """Test that capacity never goes negative even with excessive PTO."""
        # PTO for all working days plus excessive partial hours
        ptos = []
        # Add full day PTO for all 10 working days
        for day in range(8, 20):  # Jan 8-19
            ptos.append(PTOEntry(name="John Doe", date=date(2024, 1, day), hours=8))

        # Add excessive partial PTO
        ptos.append(PTOEntry(name="John Doe", date=date(2024, 1, 15), hours=100))

        capacity = calculator.calculate_member_capacity(
            member_john,
            sprint,
            location_beijing,
            ptos
        )

        assert capacity == 0.0  # Never negative
