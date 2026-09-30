"""Read Jira tasks from a CSV whose Estimate column is in hours."""

import csv
from io import StringIO
import re
from typing import List

from scrum_capacity_calculator.models import JiraTask


class JiraParser:
    FIELD_ALIASES = {
        "issue_key": {"issuekey", "key"},
        "assignee": {"assignee", "assigneename", "assignedto", "owner"},
        "sprint": {"sprint", "sprintname", "iteration"},
        "estimate": {
            "estimate",
            "estimatehours",
            "estimateh",
            "estimateinhours",
            "estimatedhours",
            "originalestimatehours",
            "originalestimateinhours",
            "timeestimatehours",
            "hours",
        },
        "summary": {"summary", "issuesummary", "title"},
    }

    def parse_csv(self, csv_content: str) -> List[JiraTask]:
        try:
            content = csv_content.lstrip("\ufeff")
            try:
                dialect = csv.Sniffer().sniff(content[:8192], delimiters=",;\t")
            except csv.Error:
                dialect = csv.excel()
                header = next((line for line in content.splitlines() if line.strip()), "")
                delimiter = max((",", ";", "\t"), key=header.count)
                if header.count(delimiter):
                    dialect.delimiter = delimiter
            reader = csv.DictReader(StringIO(content), dialect=dialect)
            columns = reader.fieldnames or []
            mapped = {}
            for column in columns:
                normalized = self._normalize_header(column)
                field = next(
                    (name for name, aliases in self.FIELD_ALIASES.items() if normalized in aliases),
                    None,
                )
                if field:
                    if field in mapped:
                        raise ValueError(f"CSV has more than one column for '{field}'")
                    mapped[field] = column

            required = {"issue_key", "assignee", "sprint", "estimate"}
            missing = required - set(mapped)
            if missing:
                raise ValueError(
                    f"Missing required columns: {', '.join(sorted(self._display_name(name) for name in missing))}. "
                    f"Available columns: {', '.join(columns)}"
                )

            tasks = []
            seen = set()
            for row_number, raw_row in enumerate(reader, start=2):
                if None in raw_row:
                    raise ValueError(f"Row {row_number} has more values than headers")
                key = (raw_row.get(mapped["issue_key"]) or "").strip()
                if not key:
                    raise ValueError(f"Row {row_number}: Issue Key is required")
                raw_estimate = (raw_row.get(mapped["estimate"]) or "").strip()
                try:
                    estimate = self._parse_estimate(raw_estimate, dialect.delimiter)
                    task = JiraTask(
                        issue_key=key,
                        summary=(raw_row.get(mapped.get("summary", "")) or "").strip(),
                        assignee=(raw_row.get(mapped["assignee"]) or "").strip() or None,
                        sprint=(raw_row.get(mapped["sprint"]) or "").strip(),
                        estimate=estimate,
                    )
                except (TypeError, ValueError) as error:
                    raise ValueError(
                        f"Error parsing row {row_number}: Invalid estimate value "
                        f"'{raw_estimate}' for {key}: {error}"
                    ) from error
                identity = (task.issue_key, task.sprint)
                if identity in seen:
                    raise ValueError(f"Row {row_number}: Duplicate issue {task.issue_key} in Sprint '{task.sprint}'")
                seen.add(identity)
                tasks.append(task)
            return tasks
        except csv.Error as error:
            raise ValueError(f"Failed to parse CSV: {error}") from error

    @staticmethod
    def _normalize_header(value: str) -> str:
        return re.sub(r"[^a-z0-9]", "", (value or "").strip().lower())

    @staticmethod
    def _display_name(field: str) -> str:
        return {
            "issue_key": "Issue Key",
            "assignee": "Assignee",
            "sprint": "Sprint",
            "estimate": "Estimate",
        }[field]

    @staticmethod
    def _parse_estimate(value: str, delimiter: str) -> float:
        if not value:
            return 0.0
        if delimiter != "," and re.fullmatch(r"\d+,\d{1,2}", value):
            value = value.replace(",", ".")
        return float(value)

    def validate_single_assignee(self, tasks: List[JiraTask]) -> List[str]:
        return [
            f"{task.issue_key}: Multiple assignees detected ('{task.assignee}')."
            for task in tasks
            if task.assignee and "," in task.assignee
        ]
