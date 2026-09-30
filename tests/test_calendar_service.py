"""Tests for calendar service."""

import pytest
from datetime import date
from scrum_capacity_calculator.core.calendar_service import CalendarService


class TestCalendarService:
    """Test calendar service working day calculations."""

    def test_working_days_no_holidays_no_pto(self):
        """Test working days with no holidays or PTO."""
        service = CalendarService()

        # Jan 8-19, 2024 (Mon-Fri, Mon-Fri) = 10 working days
        start = date(2024, 1, 8)
        end = date(2024, 1, 19)

        working_days = service.get_working_days(start, end)

        assert working_days == 10

    def test_working_days_with_holidays(self):
        """Test working days with holidays."""
        service = CalendarService()

        start = date(2024, 1, 8)
        end = date(2024, 1, 19)
        holidays = {date(2024, 1, 10)}  # Wednesday

        working_days = service.get_working_days(start, end, holidays)

        assert working_days == 9  # 10 - 1 holiday

    def test_working_days_with_pto(self):
        """Test working days with PTO."""
        service = CalendarService()

        start = date(2024, 1, 8)
        end = date(2024, 1, 19)
        pto_dates = {date(2024, 1, 15)}  # Monday

        working_days = service.get_working_days(start, end, pto_dates=pto_dates)

        assert working_days == 9  # 10 - 1 PTO

    def test_no_double_deduction_holiday_and_pto(self):
        """Test that overlapping holiday and PTO are not double counted."""
        service = CalendarService()

        start = date(2024, 1, 8)
        end = date(2024, 1, 19)
        holidays = {date(2024, 1, 10)}
        pto_dates = {date(2024, 1, 10)}  # Same day

        working_days = service.get_working_days(start, end, holidays, pto_dates)

        assert working_days == 9  # 10 - 1 (not 8)

    def test_weekend_not_counted(self):
        """Test that weekends are not counted as working days."""
        service = CalendarService()

        # Jan 6-7, 2024 is Saturday-Sunday
        start = date(2024, 1, 6)
        end = date(2024, 1, 7)

        working_days = service.get_working_days(start, end)

        assert working_days == 0

    def test_holiday_on_weekend_no_effect(self):
        """Test that holiday on weekend doesn't affect count."""
        service = CalendarService()

        start = date(2024, 1, 8)
        end = date(2024, 1, 19)
        holidays = {date(2024, 1, 13)}  # Saturday

        working_days = service.get_working_days(start, end, holidays)

        assert working_days == 10  # No change

    def test_get_holidays_for_location_china(self):
        """Test getting holidays for China."""
        service = CalendarService()

        holidays = service.get_holidays_for_location("CN", 2024)

        # China New Year 2024 is around Feb 10
        assert any(h.month == 2 for h in holidays)

    def test_get_holidays_with_manual(self):
        """Test getting holidays with manual additions."""
        service = CalendarService()

        manual = [date(2024, 3, 15)]  # Company holiday
        holidays = service.get_holidays_for_location("CN", 2024, manual)

        assert date(2024, 3, 15) in holidays

    def test_custom_weekends(self):
        """Test calendar with custom weekend days."""
        # Friday-Saturday weekend (e.g., some Middle East countries)
        service = CalendarService(weekends=[4, 5])

        start = date(2024, 1, 8)  # Monday
        end = date(2024, 1, 14)  # Sunday

        working_days = service.get_working_days(start, end)

        # Mon, Tue, Wed, Thu, Sun = 5 days
        assert working_days == 5
