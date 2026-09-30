"""Import and export the complete team configuration as a spreadsheet-friendly CSV."""

import csv
from io import StringIO
from typing import Any


CONFIG_CSV_COLUMNS = [
    "record_type",
    "sprint_name",
    "start_date",
    "end_date",
    "name",
    "jira_name",
    "group",
    "location",
    "country_code",
    "daily_hours",
    "manual_holidays",
    "date",
    "hours",
    "dates",
]


class ConfigCsvParser:
    """Convert a tagged-row CSV into the app's regular configuration object."""

    def parse(self, content: str) -> dict[str, Any]:
        if not content or not content.strip():
            raise ValueError("Configuration CSV is empty")

        content = content.lstrip("\ufeff")
        try:
            dialect = csv.Sniffer().sniff(content[:8192], delimiters=",;\t")
        except csv.Error:
            dialect = csv.excel()
            header = next((line for line in content.splitlines() if line.strip()), "")
            delimiter = max((",", ";", "\t"), key=header.count)
            if header.count(delimiter):
                dialect.delimiter = delimiter

        reader = csv.DictReader(StringIO(content), dialect=dialect)
        if not reader.fieldnames:
            raise ValueError("Configuration CSV must include a header row")

        headers = [self._header(header) for header in reader.fieldnames]
        if len(headers) != len(set(headers)):
            raise ValueError("Configuration CSV has duplicate column names")
        if "record_type" not in headers:
            raise ValueError("Configuration CSV needs a 'record_type' column")

        config: dict[str, Any] = {
            "sprint": None,
            "locations": [],
            "team_members": [],
            "group_holidays": [],
            "ptos": [],
        }

        for row_number, raw_row in enumerate(reader, start=2):
            if None in raw_row:
                raise ValueError(f"Row {row_number} has more values than headers")
            row = {
                self._header(key): (value or "").strip()
                for key, value in raw_row.items()
                if key is not None
            }
            if not any(row.values()):
                continue

            record_type = row.get("record_type", "").lower().replace(" ", "_")
            if record_type in {"team_member", "team_members"}:
                record_type = "member"

            if record_type == "sprint":
                if config["sprint"] is not None:
                    raise ValueError(f"Row {row_number}: only one Sprint record is allowed")
                config["sprint"] = {
                    "sprint_name": row.get("sprint_name", ""),
                    "start_date": row.get("start_date", ""),
                    "end_date": row.get("end_date", ""),
                }
            elif record_type == "location":
                config["locations"].append({
                    "name": row.get("name", ""),
                    "country_code": row.get("country_code", ""),
                    "manual_holidays": self._dates(row.get("manual_holidays", "")),
                })
            elif record_type == "member":
                config["team_members"].append({
                    "name": row.get("name", ""),
                    "jira_name": row.get("jira_name", ""),
                    "group": row.get("group", "Team"),
                    "location": row.get("location", ""),
                    "daily_hours": row.get("daily_hours", ""),
                })
            elif record_type == "group_holiday":
                config["group_holidays"].append({
                    "group": row.get("group", ""),
                    "location": row.get("location", ""),
                    "dates": self._dates(row.get("dates", "")),
                })
            elif record_type == "pto":
                config["ptos"].append({
                    "name": row.get("name", ""),
                    "date": row.get("date", ""),
                    "hours": row.get("hours", ""),
                })
            else:
                raise ValueError(
                    f"Row {row_number}: unknown record_type '{row.get('record_type', '')}'. "
                    "Use sprint, location, member, group_holiday, or pto."
                )

        if config["sprint"] is None:
            raise ValueError("Configuration CSV must contain one Sprint record")
        return config

    @staticmethod
    def _header(value: str) -> str:
        return (value or "").strip().lower().replace(" ", "_")

    @staticmethod
    def _dates(value: str) -> list[str]:
        return [part.strip() for part in value.split("|") if part.strip()]


def serialize_config_csv(config: dict[str, Any]) -> str:
    """Serialize a configuration object using ConfigCsvParser's row format."""
    output = StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=CONFIG_CSV_COLUMNS, lineterminator="\r\n")
    writer.writeheader()

    sprint = config.get("sprint", {})
    writer.writerow({
        "record_type": "sprint",
        "sprint_name": sprint.get("sprint_name", ""),
        "start_date": sprint.get("start_date", ""),
        "end_date": sprint.get("end_date", ""),
    })
    for location in config.get("locations", []):
        writer.writerow({
            "record_type": "location",
            "name": location.get("name", ""),
            "country_code": location.get("country_code", ""),
            "manual_holidays": "|".join(location.get("manual_holidays", [])),
        })
    for member in config.get("team_members", []):
        writer.writerow({
            "record_type": "member",
            "name": member.get("name", ""),
            "jira_name": member.get("jira_name", ""),
            "group": member.get("group", "Team"),
            "location": member.get("location", ""),
            "daily_hours": member.get("daily_hours", ""),
        })
    for rule in config.get("group_holidays", []):
        writer.writerow({
            "record_type": "group_holiday",
            "group": rule.get("group", ""),
            "location": rule.get("location", ""),
            "dates": "|".join(rule.get("dates", [])),
        })
    for pto in config.get("ptos", []):
        writer.writerow({
            "record_type": "pto",
            "name": pto.get("name", ""),
            "date": pto.get("date", ""),
            "hours": pto.get("hours", ""),
        })
    return output.getvalue()
