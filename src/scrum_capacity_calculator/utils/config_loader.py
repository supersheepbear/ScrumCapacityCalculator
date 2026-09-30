"""Configuration loader and parser."""

import json
from datetime import datetime
from typing import Dict, Any, List, Tuple
from pathlib import Path

from scrum_capacity_calculator.models import TeamMember, Sprint, PTOEntry, Location
from scrum_capacity_calculator.validators.config_validator import ConfigValidator


class ConfigLoader:
    """Loads and parses configuration files into domain objects."""

    def __init__(self):
        """Initialize loader."""
        self.validator = ConfigValidator()

    def load_from_file(self, file_path: str) -> Tuple[bool, Dict[str, Any], List[str]]:
        """
        Load configuration from JSON file.

        Args:
            file_path: Path to configuration file

        Returns:
            Tuple of (success, parsed_objects, errors)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            return False, {}, [f"Configuration file not found: {file_path}"]
        except Exception as e:
            return False, {}, [f"Failed to read file: {str(e)}"]

        return self.load_from_string(content)

    def load_from_string(self, json_string: str) -> Tuple[bool, Dict[str, Any], List[str]]:
        """
        Load configuration from JSON string.

        Args:
            json_string: JSON configuration string

        Returns:
            Tuple of (success, parsed_objects, errors)
            parsed_objects contains: sprint, members, locations, ptos
        """
        is_valid, config_data, errors = self.validator.validate_json_string(json_string)

        if not is_valid:
            return False, {}, errors

        try:
            parsed = self._parse_config(config_data)
            return True, parsed, errors  # errors may contain warnings
        except Exception as e:
            return False, {}, [f"Failed to parse configuration: {str(e)}"]

    def _parse_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Parse validated configuration into domain objects."""
        return {
            "sprint": self._parse_sprint(config["sprint"]),
            "members": self._parse_members(config["team_members"]),
            "locations": self._parse_locations(config["locations"]),
            "ptos": self._parse_ptos(config.get("ptos", [])),
        }

    def _parse_sprint(self, sprint_data: Dict[str, Any]) -> Sprint:
        """Parse sprint data."""
        return Sprint(
            sprint_name=sprint_data["sprint_name"],
            start_date=self._parse_date(sprint_data["start_date"]),
            end_date=self._parse_date(sprint_data["end_date"])
        )

    def _parse_members(self, members_data: List[Dict[str, Any]]) -> List[TeamMember]:
        """Parse team members data."""
        members = []
        for data in members_data:
            member = TeamMember(
                name=data["name"],
                daily_hours=float(data["daily_hours"]),
                location=data["location"],
                jira_name=data.get("jira_name")
            )
            members.append(member)
        return members

    def _parse_locations(self, locations_data: List[Dict[str, Any]]) -> List[Location]:
        """Parse locations data."""
        locations = []
        for data in locations_data:
            manual_holidays = []
            if "manual_holidays" in data and data["manual_holidays"]:
                manual_holidays = [
                    self._parse_date(h) for h in data["manual_holidays"]
                ]

            location = Location(
                name=data["name"],
                country_code=data["country_code"],
                manual_holidays=manual_holidays
            )
            locations.append(location)
        return locations

    def _parse_ptos(self, ptos_data: List[Dict[str, Any]]) -> List[PTOEntry]:
        """Parse PTO entries."""
        ptos = []
        for data in ptos_data:
            pto = PTOEntry(
                name=data["name"],
                date=self._parse_date(data["date"]),
                hours=float(data["hours"])
            )
            ptos.append(pto)
        return ptos

    def _parse_date(self, date_str: str):
        """Parse date string in YYYY-MM-DD format."""
        return datetime.strptime(date_str, "%Y-%m-%d").date()

    def load_system_config(self, file_path: str = None) -> Dict[str, Any]:
        """
        Load system configuration.

        Args:
            file_path: Path to system config file. If None, uses default.

        Returns:
            System configuration dict
        """
        if file_path is None:
            # Default system config path
            file_path = Path(__file__).parent.parent.parent / "config" / "system_config.json"

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            # Return defaults if loading fails
            return {
                "capacity_thresholds": {
                    "normal_max": 0.8,
                    "warning_max": 1.0
                },
                "date_format": "YYYY-MM-DD",
                "default_daily_hours": 8,
                "default_weekends": [5, 6],
                "report": {
                    "show_day_equivalents": True,
                    "hours_per_day_for_display": 8,
                    "default_sort": "load_rate_desc"
                }
            }
