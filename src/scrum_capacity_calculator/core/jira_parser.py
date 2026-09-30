"""Read Jira tasks from a CSV whose Estimate column is in hours."""

import csv
from io import StringIO
from typing import List

from scrum_capacity_calculator.models import JiraTask


class JiraParser:
    REQUIRED_COLUMNS = {"Issue Key", "Assignee", "Sprint", "Estimate"}

    def parse_csv(self, csv_content: str) -> List[JiraTask]:
        try:
            reader = csv.DictReader(StringIO(csv_content.lstrip("\ufeff")))
            columns = reader.fieldnames or []
            mapped = [column.strip() for column in columns]
            missing = self.REQUIRED_COLUMNS - set(mapped)
            if missing:
                raise ValueError(
                    f"Missing required columns: {', '.join(sorted(missing))}. "
                    f"Available columns: {', '.join(columns)}"
                )
            if len(mapped) != len(set(mapped)):
                raise ValueError("CSV has duplicate column names")

            tasks = []
            seen = set()
            for row_number, raw_row in enumerate(reader, start=2):
                if None in raw_row:
                    raise ValueError(f"Row {row_number} has more values than headers")
                row = dict(zip(mapped, (raw_row[column] for column in columns)))
                key = (row["Issue Key"] or "").strip()
                if not key:
                    raise ValueError(f"Row {row_number}: Issue Key is required")
                raw_estimate = (row["Estimate"] or "").strip()
                try:
                    estimate = float(raw_estimate) if raw_estimate else 0.0
                    task = JiraTask(
                        issue_key=key,
                        summary=(row.get("Summary") or "").strip(),
                        assignee=(row["Assignee"] or "").strip() or None,
                        sprint=(row["Sprint"] or "").strip(),
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

    def validate_single_assignee(self, tasks: List[JiraTask]) -> List[str]:
        return [
            f"{task.issue_key}: Multiple assignees detected ('{task.assignee}')."
            for task in tasks
            if task.assignee and "," in task.assignee
        ]
