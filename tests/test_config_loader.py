"""Tests for config loader."""

import pytest
import json
from pathlib import Path
from scrum_capacity_calculator.utils.config_loader import ConfigLoader


class TestConfigLoader:
    """Test configuration loader."""

    @pytest.fixture
    def loader(self):
        """Create loader instance."""
        return ConfigLoader()

    @pytest.fixture
    def valid_config_json(self):
        """Valid configuration as JSON string."""
        return json.dumps({
            "sprint": {
                "sprint_name": "2024-Q1-Sprint-1",
                "start_date": "2024-01-08",
                "end_date": "2024-01-19"
            },
            "team_members": [
                {
                    "name": "John Doe",
                    "jira_name": "john.doe",
                    "daily_hours": 8,
                    "location": "Beijing"
                }
            ],
            "locations": [
                {
                    "name": "Beijing",
                    "country_code": "CN",
                    "manual_holidays": ["2024-01-15"]
                }
            ],
            "ptos": [
                {
                    "name": "John Doe",
                    "date": "2024-01-10",
                    "hours": 8
                }
            ]
        })

    def test_load_from_string_success(self, loader, valid_config_json):
        """Test loading valid configuration from string."""
        success, parsed, errors = loader.load_from_string(valid_config_json)

        assert success is True
        assert "sprint" in parsed
        assert "members" in parsed
        assert "locations" in parsed
        assert "ptos" in parsed

        # Check sprint parsing
        sprint = parsed["sprint"]
        assert sprint.sprint_name == "2024-Q1-Sprint-1"
        assert str(sprint.start_date) == "2024-01-08"

        # Check members parsing
        assert len(parsed["members"]) == 1
        assert parsed["members"][0].name == "John Doe"
        assert parsed["members"][0].daily_hours == 8

        # Check locations parsing
        assert len(parsed["locations"]) == 1
        assert parsed["locations"][0].name == "Beijing"
        assert parsed["locations"][0].country_code == "CN"

        # Check PTO parsing
        assert len(parsed["ptos"]) == 1
        assert parsed["ptos"][0].name == "John Doe"
        assert parsed["ptos"][0].hours == 8

    def test_load_invalid_json(self, loader):
        """Test loading invalid JSON."""
        invalid_json = "{ invalid json"

        success, parsed, errors = loader.load_from_string(invalid_json)

        assert success is False
        assert len(errors) > 0

    def test_load_missing_required_field(self, loader):
        """Test loading config with missing required field."""
        invalid_config = json.dumps({
            "sprint": {
                "sprint_name": "Test",
                "start_date": "2024-01-08"
                # Missing end_date
            },
            "team_members": [],
            "locations": []
        })

        success, parsed, errors = loader.load_from_string(invalid_config)

        assert success is False
        assert len(errors) > 0

    def test_load_with_default_jira_name(self, loader):
        """Test that jira_name defaults to name if not provided."""
        config = json.dumps({
            "sprint": {
                "sprint_name": "Test Sprint",
                "start_date": "2024-01-08",
                "end_date": "2024-01-19"
            },
            "team_members": [
                {
                    "name": "John Doe",
                    # No jira_name provided
                    "daily_hours": 8,
                    "location": "Beijing"
                }
            ],
            "locations": [
                {"name": "Beijing", "country_code": "CN", "manual_holidays": []}
            ]
        })

        success, parsed, errors = loader.load_from_string(config)

        assert success is True
        assert parsed["members"][0].jira_name == "John Doe"

    def test_load_from_file(self, loader, tmp_path, valid_config_json):
        """Test loading configuration from file."""
        # Create temporary config file
        config_file = tmp_path / "test_config.json"
        config_file.write_text(valid_config_json)

        success, parsed, errors = loader.load_from_file(str(config_file))

        assert success is True
        assert "sprint" in parsed
        assert parsed["sprint"].sprint_name == "2024-Q1-Sprint-1"

    def test_load_from_nonexistent_file(self, loader):
        """Test loading from non-existent file."""
        success, parsed, errors = loader.load_from_file("/nonexistent/file.json")

        assert success is False
        assert len(errors) > 0
        assert any("not found" in err.lower() for err in errors)

    def test_parse_manual_holidays(self, loader):
        """Test parsing manual holidays."""
        config = json.dumps({
            "sprint": {
                "sprint_name": "Test Sprint",
                "start_date": "2024-01-08",
                "end_date": "2024-01-19"
            },
            "team_members": [
                {"name": "John", "daily_hours": 8, "location": "Beijing"}
            ],
            "locations": [
                {
                    "name": "Beijing",
                    "country_code": "CN",
                    "manual_holidays": ["2024-02-10", "2024-02-11"]
                }
            ]
        })

        success, parsed, errors = loader.load_from_string(config)

        assert success is True
        location = parsed["locations"][0]
        assert len(location.manual_holidays) == 2
        assert str(location.manual_holidays[0]) == "2024-02-10"

    def test_parse_empty_ptos(self, loader):
        """Test parsing config with no PTOs."""
        config = json.dumps({
            "sprint": {
                "sprint_name": "Test Sprint",
                "start_date": "2024-01-08",
                "end_date": "2024-01-19"
            },
            "team_members": [
                {"name": "John", "daily_hours": 8, "location": "Beijing"}
            ],
            "locations": [
                {"name": "Beijing", "country_code": "CN", "manual_holidays": []}
            ]
            # No ptos field
        })

        success, parsed, errors = loader.load_from_string(config)

        assert success is True
        assert len(parsed["ptos"]) == 0
