"""Jira CSV parser."""

import pandas as pd
from typing import List, Dict, Optional
from io import StringIO
from scrum_capacity_calculator.models import JiraTask


class JiraParser:
    """Parses Jira CSV exports into task objects."""

    REQUIRED_COLUMNS = ["Issue Key", "Assignee", "Sprint", "Estimate"]

    def __init__(self, column_mapping: Dict[str, str] = None):
        """
        Initialize parser.

        Args:
            column_mapping: Optional mapping of CSV column names to standard names.
                          E.g., {"Story Points": "Estimate"}
        """
        self.column_mapping = column_mapping or {}

    def parse_csv(self, csv_content: str) -> List[JiraTask]:
        """
        Parse Jira CSV content into tasks.

        Args:
            csv_content: CSV file content as string

        Returns:
            List of JiraTask objects

        Raises:
            ValueError: If required columns are missing or data is invalid
        """
        # Read CSV
        try:
            df = pd.read_csv(StringIO(csv_content))
        except Exception as e:
            raise ValueError(f"Failed to parse CSV: {str(e)}")

        # Apply column mapping
        df = df.rename(columns=self.column_mapping)

        # Validate required columns
        missing_columns = set(self.REQUIRED_COLUMNS) - set(df.columns)
        if missing_columns:
            raise ValueError(
                f"Missing required columns: {', '.join(missing_columns)}. "
                f"Available columns: {', '.join(df.columns)}"
            )

        # Parse tasks
        tasks = []
        for idx, row in df.iterrows():
            try:
                task = self._parse_row(row)
                tasks.append(task)
            except Exception as e:
                raise ValueError(f"Error parsing row {idx + 2}: {str(e)}")

        return tasks

    def _parse_row(self, row: pd.Series) -> JiraTask:
        """Parse a single CSV row into a JiraTask."""
        issue_key = str(row["Issue Key"]).strip()

        # Handle missing or empty assignee
        assignee = row["Assignee"]
        if pd.isna(assignee) or str(assignee).strip() == "":
            assignee = None
        else:
            assignee = str(assignee).strip()

        sprint = str(row["Sprint"]).strip()

        # Handle estimate
        estimate = row["Estimate"]
        if pd.isna(estimate):
            estimate = 0.0
        else:
            try:
                estimate = float(estimate)
            except (ValueError, TypeError):
                raise ValueError(
                    f"Invalid estimate value '{estimate}' for {issue_key}"
                )

        # Get summary if available
        summary = ""
        if "Summary" in row.index:
            summary = str(row["Summary"]) if not pd.isna(row["Summary"]) else ""

        return JiraTask(
            issue_key=issue_key,
            summary=summary,
            assignee=assignee,
            sprint=sprint,
            estimate=estimate
        )

    def validate_single_assignee(self, tasks: List[JiraTask]) -> List[str]:
        """
        Check for tasks with multiple assignees (not supported).

        Args:
            tasks: List of tasks to check

        Returns:
            List of error messages for tasks with issues
        """
        errors = []

        # Check for comma-separated assignees (common multi-assignee format)
        for task in tasks:
            if task.assignee and "," in task.assignee:
                errors.append(
                    f"{task.issue_key}: Multiple assignees detected ('{task.assignee}'). "
                    f"Please split the task or assign to a single person."
                )

        return errors

    def get_column_suggestions(self, csv_content: str) -> Dict[str, List[str]]:
        """
        Suggest column mappings based on common patterns.

        Args:
            csv_content: CSV file content

        Returns:
            Dict of {standard_name: [possible_column_names]}
        """
        try:
            df = pd.read_csv(StringIO(csv_content))
        except Exception:
            return {}

        suggestions = {}
        columns = df.columns.tolist()

        # Common patterns for each required field
        patterns = {
            "Issue Key": ["key", "issue", "ticket", "id"],
            "Assignee": ["assignee", "assigned", "owner", "responsible"],
            "Sprint": ["sprint", "iteration"],
            "Estimate": ["estimate", "story points", "points", "hours", "effort"],
        }

        for standard_name, keywords in patterns.items():
            matches = []
            for col in columns:
                col_lower = col.lower()
                if any(keyword in col_lower for keyword in keywords):
                    matches.append(col)
            if matches:
                suggestions[standard_name] = matches

        return suggestions
