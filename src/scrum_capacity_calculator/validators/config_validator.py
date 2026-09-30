"""Configuration validator."""

from datetime import datetime, date
from typing import Dict, List, Any, Tuple
import json


class ConfigValidator:
    """Validates team configuration data."""

    def __init__(self):
        """Initialize validator."""
        self.errors = []
        self.warnings = []

    def validate_config(self, config_data: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
        """
        Validate complete configuration.

        Args:
            config_data: Configuration dictionary

        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        self.errors = []
        self.warnings = []

        # Validate structure
        self._validate_structure(config_data)

        if not self.errors:
            # Validate each section
            self._validate_sprint(config_data.get("sprint", {}))
            self._validate_team_members(config_data.get("team_members", []))
            self._validate_locations(config_data.get("locations", []))
            self._validate_ptos(config_data.get("ptos", []))

        is_valid = len(self.errors) == 0
        return is_valid, self.errors, self.warnings

    def _validate_structure(self, config: Dict[str, Any]):
        """Validate top-level structure."""
        required_keys = ["sprint", "team_members", "locations"]

        for key in required_keys:
            if key not in config:
                self.errors.append(f"Missing required section: '{key}'")

    def _validate_sprint(self, sprint: Dict[str, Any]):
        """Validate sprint configuration."""
        if not sprint:
            return

        # Check required fields
        required = ["sprint_name", "start_date", "end_date"]
        for field in required:
            if field not in sprint:
                self.errors.append(f"Sprint missing required field: '{field}'")
                return

        # Validate sprint name
        if not sprint["sprint_name"] or not sprint["sprint_name"].strip():
            self.errors.append("Sprint name cannot be empty")

        # Validate dates
        try:
            start_date = self._parse_date(sprint["start_date"])
            end_date = self._parse_date(sprint["end_date"])

            if end_date <= start_date:
                self.errors.append(
                    f"Sprint end_date ({sprint['end_date']}) must be after "
                    f"start_date ({sprint['start_date']})"
                )

            # Check duration
            duration = (end_date - start_date).days + 1
            if duration != 14:
                self.warnings.append(
                    f"Sprint duration is {duration} days (expected 14 days)"
                )

        except ValueError as e:
            self.errors.append(f"Invalid sprint date: {str(e)}")

    def _validate_team_members(self, members: List[Dict[str, Any]]):
        """Validate team members."""
        if not members:
            self.errors.append("At least one team member is required")
            return

        names = set()
        jira_names = set()

        for idx, member in enumerate(members):
            prefix = f"Team member {idx + 1}"

            # Required fields
            if "name" not in member:
                self.errors.append(f"{prefix}: missing 'name'")
                continue
            if "daily_hours" not in member:
                self.errors.append(f"{prefix}: missing 'daily_hours'")
                continue
            if "location" not in member:
                self.errors.append(f"{prefix}: missing 'location'")
                continue

            # Validate name
            name = member["name"]
            if not name or not name.strip():
                self.errors.append(f"{prefix}: name cannot be empty")
            elif name in names:
                self.errors.append(f"{prefix}: duplicate name '{name}'")
            else:
                names.add(name)

            # Validate daily_hours
            try:
                hours = float(member["daily_hours"])
                if hours <= 0 or hours > 24:
                    self.errors.append(
                        f"{prefix} ({name}): daily_hours must be between 0 and 24, got {hours}"
                    )
            except (ValueError, TypeError):
                self.errors.append(
                    f"{prefix} ({name}): daily_hours must be a number"
                )

            # Validate jira_name if provided
            if "jira_name" in member and member["jira_name"]:
                jira_name = member["jira_name"]
                if jira_name in jira_names:
                    self.errors.append(
                        f"{prefix} ({name}): duplicate jira_name '{jira_name}'"
                    )
                else:
                    jira_names.add(jira_name)

    def _validate_locations(self, locations: List[Dict[str, Any]]):
        """Validate locations."""
        if not locations:
            self.errors.append("At least one location is required")
            return

        location_names = set()

        for idx, location in enumerate(locations):
            prefix = f"Location {idx + 1}"

            # Required fields
            if "name" not in location:
                self.errors.append(f"{prefix}: missing 'name'")
                continue
            if "country_code" not in location:
                self.errors.append(f"{prefix}: missing 'country_code'")
                continue

            # Validate name
            name = location["name"]
            if not name or not name.strip():
                self.errors.append(f"{prefix}: name cannot be empty")
            elif name in location_names:
                self.errors.append(f"{prefix}: duplicate location name '{name}'")
            else:
                location_names.add(name)

            # Validate country code
            if not location["country_code"] or not location["country_code"].strip():
                self.errors.append(f"{prefix} ({name}): country_code cannot be empty")

            # Validate manual_holidays if provided
            if "manual_holidays" in location:
                holidays = location["manual_holidays"]
                if not isinstance(holidays, list):
                    self.errors.append(
                        f"{prefix} ({name}): manual_holidays must be a list"
                    )
                else:
                    for h_idx, holiday in enumerate(holidays):
                        try:
                            self._parse_date(holiday)
                        except ValueError:
                            self.errors.append(
                                f"{prefix} ({name}): invalid holiday date at "
                                f"index {h_idx}: '{holiday}'"
                            )

    def _validate_ptos(self, ptos: List[Dict[str, Any]]):
        """Validate PTO entries."""
        for idx, pto in enumerate(ptos):
            prefix = f"PTO {idx + 1}"

            # Required fields
            if "name" not in pto:
                self.errors.append(f"{prefix}: missing 'name'")
                continue
            if "date" not in pto:
                self.errors.append(f"{prefix}: missing 'date'")
                continue
            if "hours" not in pto:
                self.errors.append(f"{prefix}: missing 'hours'")
                continue

            # Validate date
            try:
                self._parse_date(pto["date"])
            except ValueError:
                self.errors.append(
                    f"{prefix} ({pto['name']}): invalid date '{pto['date']}'"
                )

            # Validate hours
            try:
                hours = float(pto["hours"])
                if hours <= 0:
                    self.errors.append(
                        f"{prefix} ({pto['name']}): hours must be positive, got {hours}"
                    )
            except (ValueError, TypeError):
                self.errors.append(
                    f"{prefix} ({pto['name']}): hours must be a number"
                )

    def _parse_date(self, date_str: str) -> date:
        """
        Parse date string in YYYY-MM-DD format.

        Args:
            date_str: Date string

        Returns:
            date object

        Raises:
            ValueError: If date format is invalid
        """
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            raise ValueError(
                f"Expected format YYYY-MM-DD, got '{date_str}'"
            )

    def validate_json_string(self, json_string: str) -> Tuple[bool, Dict[str, Any], List[str]]:
        """
        Validate JSON string and parse it.

        Args:
            json_string: JSON configuration string

        Returns:
            Tuple of (is_valid, parsed_config, errors)
        """
        try:
            config = json.loads(json_string)
        except json.JSONDecodeError as e:
            return False, {}, [f"Invalid JSON: {str(e)}"]

        is_valid, errors, warnings = self.validate_config(config)
        all_messages = errors + warnings

        return is_valid, config, all_messages
