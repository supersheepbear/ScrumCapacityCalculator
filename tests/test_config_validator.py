"""Tests for config validator."""

import pytest
import json
from scrum_capacity_calculator.validators.config_validator import ConfigValidator


class TestConfigValidator:
    """Test configuration validation."""

    @pytest.fixture
    def validator(self):
        """Create validator instance."""
        return ConfigValidator()

    def test_validate_valid_config(self, validator):
        """Test validating a valid configuration."""
        config = {
            "sprint": {
                "sprint_name": "Test Sprint",
                "start_date": "2024-01-08",
                "end_date": "2024-01-19"
            },
            "team_members": [
                {
                    "name": "John Doe",
                    "daily_hours": 8,
                    "location": "Beijing"
                }
            ],
            "locations": [
                {
                    "name": "Beijing",
                    "country_code": "CN",
                    "manual_holidays": []
                }
            ],
            "ptos": []
        }

        is_valid, errors, warnings = validator.validate_config(config)

        assert is_valid is True
        assert len(errors) == 0

    def test_validate_missing_sprint(self, validator):
        """Test validation fails when sprint is missing."""
        config = {
            "team_members": [],
            "locations": []
        }

        is_valid, errors, warnings = validator.validate_config(config)

        assert is_valid is False
        assert any("sprint" in err.lower() for err in errors)

    def test_validate_invalid_date_format(self, validator):
        """Test validation fails with invalid date format."""
        config = {
            "sprint": {
                "sprint_name": "Test Sprint",
                "start_date": "01/08/2024",  # Wrong format
                "end_date": "2024-01-19"
            },
            "team_members": [{"name": "John", "daily_hours": 8, "location": "Beijing"}],
            "locations": [{"name": "Beijing", "country_code": "CN", "manual_holidays": []}]
        }

        is_valid, errors, warnings = validator.validate_config(config)

        assert is_valid is False
        assert any("date" in err.lower() for err in errors)

    def test_validate_end_before_start(self, validator):
        """Test validation fails when end date is before start date."""
        config = {
            "sprint": {
                "sprint_name": "Test Sprint",
                "start_date": "2024-01-19",
                "end_date": "2024-01-08"  # Before start
            },
            "team_members": [{"name": "John", "daily_hours": 8, "location": "Beijing"}],
            "locations": [{"name": "Beijing", "country_code": "CN", "manual_holidays": []}]
        }

        is_valid, errors, warnings = validator.validate_config(config)

        assert is_valid is False
        assert any("end_date" in err and "after" in err for err in errors)

    def test_validate_duplicate_member_names(self, validator):
        """Test validation fails with duplicate member names."""
        config = {
            "sprint": {
                "sprint_name": "Test Sprint",
                "start_date": "2024-01-08",
                "end_date": "2024-01-19"
            },
            "team_members": [
                {"name": "John Doe", "daily_hours": 8, "location": "Beijing"},
                {"name": "John Doe", "daily_hours": 6, "location": "Shanghai"}
            ],
            "locations": [
                {"name": "Beijing", "country_code": "CN", "manual_holidays": []},
                {"name": "Shanghai", "country_code": "CN", "manual_holidays": []}
            ]
        }

        is_valid, errors, warnings = validator.validate_config(config)

        assert is_valid is False
        assert any("duplicate" in err.lower() and "john doe" in err.lower() for err in errors)

    def test_validate_invalid_daily_hours(self, validator):
        """Test validation fails with invalid daily hours."""
        config = {
            "sprint": {
                "sprint_name": "Test Sprint",
                "start_date": "2024-01-08",
                "end_date": "2024-01-19"
            },
            "team_members": [
                {"name": "John Doe", "daily_hours": 25, "location": "Beijing"}  # > 24
            ],
            "locations": [
                {"name": "Beijing", "country_code": "CN", "manual_holidays": []}
            ]
        }

        is_valid, errors, warnings = validator.validate_config(config)

        assert is_valid is False
        assert any("daily_hours" in err and "24" in err for err in errors)

    def test_validate_json_string(self, validator):
        """Test validating JSON string."""
        config_str = json.dumps({
            "sprint": {
                "sprint_name": "Test Sprint",
                "start_date": "2024-01-08",
                "end_date": "2024-01-19"
            },
            "team_members": [{"name": "John", "daily_hours": 8, "location": "Beijing"}],
            "locations": [{"name": "Beijing", "country_code": "CN", "manual_holidays": []}],
            "ptos": []
        })

        is_valid, config, errors = validator.validate_json_string(config_str)

        assert is_valid is True
        # May have warnings about sprint duration, but no errors
        assert config["sprint"]["sprint_name"] == "Test Sprint"

    def test_validate_invalid_json(self, validator):
        """Test validation fails with invalid JSON."""
        config_str = "{ invalid json "

        is_valid, config, errors = validator.validate_json_string(config_str)

        assert is_valid is False
        assert len(errors) > 0
        assert any("json" in err.lower() for err in errors)

    def test_validate_empty_member_name(self, validator):
        """Test validation fails with empty member name."""
        config = {
            "sprint": {
                "sprint_name": "Test Sprint",
                "start_date": "2024-01-08",
                "end_date": "2024-01-19"
            },
            "team_members": [
                {"name": "", "daily_hours": 8, "location": "Beijing"}
            ],
            "locations": [
                {"name": "Beijing", "country_code": "CN", "manual_holidays": []}
            ]
        }

        is_valid, errors, warnings = validator.validate_config(config)

        assert is_valid is False
        assert any("name" in err.lower() and "empty" in err.lower() for err in errors)

    def test_validate_sprint_duration_warning(self, validator):
        """Test warning for non-standard sprint duration."""
        config = {
            "sprint": {
                "sprint_name": "Test Sprint",
                "start_date": "2024-01-08",
                "end_date": "2024-01-15"  # Only 8 days
            },
            "team_members": [{"name": "John", "daily_hours": 8, "location": "Beijing"}],
            "locations": [{"name": "Beijing", "country_code": "CN", "manual_holidays": []}]
        }

        is_valid, errors, warnings = validator.validate_config(config)

        assert is_valid is True
        assert len(warnings) > 0
        assert any("duration" in warn.lower() for warn in warnings)
