"""CSV import and export cases for the complete team setup."""

import json

from scrum_capacity_calculator.core.config_csv import ConfigCsvParser, serialize_config_csv
from scrum_capacity_calculator.utils.config_loader import ConfigLoader


def test_configuration_csv_round_trips_all_record_types():
    config = {
        "sprint": {"sprint_name": "Sprint 1", "start_date": "2026-10-05", "end_date": "2026-10-16"},
        "locations": [{"name": "New York", "country_code": "US", "manual_holidays": ["2026-10-12"]}],
        "team_members": [{
            "name": "Alice Smith", "jira_name": "alice.smith", "group": "Engineering",
            "location": "New York", "daily_hours": 7.5,
        }],
        "group_holidays": [{"group": "Engineering", "location": "New York", "dates": ["2026-10-13"]}],
        "ptos": [{"name": "Alice Smith", "date": "2026-10-14", "hours": 3}],
    }

    parsed = ConfigCsvParser().parse(serialize_config_csv(config))
    valid, _, messages = ConfigLoader().load_from_string(json.dumps(parsed))

    assert valid, messages
    assert parsed["sprint"] == config["sprint"]
    assert parsed["locations"][0]["manual_holidays"] == ["2026-10-12"]
    assert parsed["team_members"][0]["daily_hours"] == "7.5"
    assert parsed["group_holidays"] == config["group_holidays"]
    assert parsed["ptos"][0]["hours"] == "3"


def test_configuration_csv_accepts_semicolon_delimiter_and_header_spaces():
    content = (
        "Record Type;Sprint Name;Start Date;End Date;Name;Jira Name;Group;Location;"
        "Country Code;Daily Hours;Manual Holidays;Date;Hours;Dates\n"
        "sprint;Sprint 1;2026-10-05;2026-10-16;;;;;;;;;;\n"
        "location;;;;New York;;;;US;;;;;\n"
        "member;;;;Alice;alice;Engineering;New York;;8;;;;\n"
    )

    parsed = ConfigCsvParser().parse(content)

    assert parsed["sprint"]["sprint_name"] == "Sprint 1"
    assert parsed["locations"][0]["name"] == "New York"
    assert parsed["team_members"][0]["jira_name"] == "alice"
