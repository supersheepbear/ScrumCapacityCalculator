"""Tests for Jira parser."""

import pytest
from scrum_capacity_calculator.core.jira_parser import JiraParser


class TestJiraParser:
    """Test Jira CSV parser."""

    @pytest.fixture
    def parser(self):
        """Create parser instance."""
        return JiraParser()

    def test_parse_valid_csv(self, parser):
        """Test parsing valid CSV."""
        csv_content = """Issue Key,Summary,Assignee,Sprint,Estimate
PROJ-1,Task 1,john.doe,Sprint-1,16
PROJ-2,Task 2,jane.smith,Sprint-1,24
PROJ-3,Task 3,bob.lee,Sprint-2,8"""

        tasks = parser.parse_csv(csv_content)

        assert len(tasks) == 3
        assert tasks[0].issue_key == "PROJ-1"
        assert tasks[0].assignee == "john.doe"
        assert tasks[0].sprint == "Sprint-1"
        assert tasks[0].estimate == 16.0

    def test_parse_csv_with_empty_assignee(self, parser):
        """Test parsing CSV with empty assignee."""
        csv_content = """Issue Key,Summary,Assignee,Sprint,Estimate
PROJ-1,Task 1,,Sprint-1,16"""

        tasks = parser.parse_csv(csv_content)

        assert len(tasks) == 1
        assert tasks[0].assignee is None

    def test_parse_csv_with_zero_estimate(self, parser):
        """Test parsing CSV with zero estimate."""
        csv_content = """Issue Key,Summary,Assignee,Sprint,Estimate
PROJ-1,Task 1,john.doe,Sprint-1,0"""

        tasks = parser.parse_csv(csv_content)

        assert len(tasks) == 1
        assert tasks[0].estimate == 0.0

    def test_parse_csv_with_empty_estimate(self, parser):
        """Test parsing CSV with empty estimate."""
        csv_content = """Issue Key,Summary,Assignee,Sprint,Estimate
PROJ-1,Task 1,john.doe,Sprint-1,"""

        tasks = parser.parse_csv(csv_content)

        assert len(tasks) == 1
        assert tasks[0].estimate == 0.0

    def test_parse_csv_missing_columns(self, parser):
        """Test parsing CSV with missing required columns."""
        csv_content = """Issue Key,Summary,Assignee
PROJ-1,Task 1,john.doe"""

        with pytest.raises(ValueError) as exc_info:
            parser.parse_csv(csv_content)

        assert "Missing required columns" in str(exc_info.value)
        assert "Sprint" in str(exc_info.value)

    def test_parse_csv_invalid_estimate(self, parser):
        """Test parsing CSV with invalid estimate."""
        csv_content = """Issue Key,Summary,Assignee,Sprint,Estimate
PROJ-1,Task 1,john.doe,Sprint-1,invalid"""

        with pytest.raises(ValueError) as exc_info:
            parser.parse_csv(csv_content)

        assert "Invalid estimate value" in str(exc_info.value)

    def test_validate_single_assignee_with_comma(self, parser):
        """Test validation catches comma-separated assignees."""
        csv_content = """Issue Key,Summary,Assignee,Sprint,Estimate
PROJ-1,Task 1,"john.doe,jane.smith",Sprint-1,16"""

        tasks = parser.parse_csv(csv_content)
        errors = parser.validate_single_assignee(tasks)

        assert len(errors) == 1
        assert "Multiple assignees detected" in errors[0]

    def test_validate_single_assignee_clean(self, parser):
        """Test validation passes with single assignees."""
        csv_content = """Issue Key,Summary,Assignee,Sprint,Estimate
PROJ-1,Task 1,john.doe,Sprint-1,16
PROJ-2,Task 2,jane.smith,Sprint-1,24"""

        tasks = parser.parse_csv(csv_content)
        errors = parser.validate_single_assignee(tasks)

        assert len(errors) == 0

    def test_duplicate_issue_in_same_sprint_is_rejected(self, parser):
        csv_content = """Issue Key,Assignee,Sprint,Estimate
PROJ-1,john.doe,Sprint-1,8
PROJ-1,john.doe,Sprint-1,8"""

        with pytest.raises(ValueError, match="Duplicate issue"):
            parser.parse_csv(csv_content)

    def test_accepts_semicolon_export_header_aliases_and_decimal_comma(self, parser):
        csv_content = "Key;Owner;Iteration;Estimate (hours);Title\nPROJ-1;alice;Sprint-1;1,5;Task"

        tasks = parser.parse_csv(csv_content)

        assert tasks[0].issue_key == "PROJ-1"
        assert tasks[0].assignee == "alice"
        assert tasks[0].summary == "Task"
        assert tasks[0].estimate == 1.5

    def test_accepts_tab_delimited_csv_with_bom(self, parser):
        csv_content = "\ufeffIssue Key\tAssignee\tSprint\tEstimate\nPROJ-1\talice\tSprint-1\t8"

        tasks = parser.parse_csv(csv_content)

        assert tasks[0].estimate == 8.0

    def test_does_not_treat_story_points_as_estimate_hours(self, parser):
        csv_content = "Issue Key,Assignee,Sprint,Story Points\nPROJ-1,alice,Sprint-1,5"

        with pytest.raises(ValueError, match="Missing required columns"):
            parser.parse_csv(csv_content)
