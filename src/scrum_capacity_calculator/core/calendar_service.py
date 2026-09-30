"""Calendar service for working day calculations."""

from datetime import date, timedelta
from typing import List, Set
import holidays as holidays_lib


class CalendarService:
    """Handles working day calculations with holidays and PTO."""

    def __init__(self, weekends: List[int] = None):
        """
        Initialize calendar service.

        Args:
            weekends: List of weekend day numbers (0=Monday, 6=Sunday).
                     Default is [5, 6] (Saturday, Sunday).
        """
        self.weekends = weekends if weekends is not None else [5, 6]

    def get_working_days(
        self,
        start_date: date,
        end_date: date,
        holidays: Set[date] = None,
        pto_dates: Set[date] = None
    ) -> int:
        """
        Calculate number of working days in a date range.

        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            holidays: Set of holiday dates
            pto_dates: Set of PTO dates

        Returns:
            Number of working days
        """
        if holidays is None:
            holidays = set()
        if pto_dates is None:
            pto_dates = set()

        # Combine holidays and PTO (no double counting)
        non_working_dates = holidays | pto_dates

        working_days = 0
        current_date = start_date

        while current_date <= end_date:
            # Check if it's a working day
            is_weekend = current_date.weekday() in self.weekends
            is_non_working = current_date in non_working_dates

            if not is_weekend and not is_non_working:
                working_days += 1

            current_date += timedelta(days=1)

        return working_days

    def get_holidays_for_location(
        self,
        country_code: str,
        year: int,
        manual_holidays: List[date] = None
    ) -> Set[date]:
        """
        Get holidays for a location.

        Args:
            country_code: ISO country code (e.g., 'CN', 'US')
            year: Year to get holidays for
            manual_holidays: Additional manual holiday dates

        Returns:
            Set of holiday dates
        """
        holiday_set = set()

        # Get auto holidays from library
        try:
            country_holidays = holidays_lib.country_holidays(country_code, years=year)
            holiday_set.update(country_holidays.keys())
        except NotImplementedError:
            # Country not supported, use manual only
            pass

        # Add manual holidays
        if manual_holidays:
            holiday_set.update(manual_holidays)

        return holiday_set

    def calculate_pto_days(
        self,
        pto_hours: float,
        daily_hours: float
    ) -> float:
        """
        Convert PTO hours to day equivalent.

        Args:
            pto_hours: Hours of PTO
            daily_hours: Member's daily work hours

        Returns:
            PTO in days
        """
        if daily_hours <= 0:
            raise ValueError("daily_hours must be positive")
        return pto_hours / daily_hours
