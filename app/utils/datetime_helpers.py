"""
Date/time utility functions for appointment slot management.
"""

from datetime import datetime, date, time, timedelta
from typing import Optional
from app.config import settings


def generate_time_slots(target_date: date) -> list[str]:
    """
    Generate all available time slots for a given date based on clinic hours.

    Args:
        target_date: The date to generate slots for.

    Returns:
        List of time strings (e.g., ["9:00 AM", "9:30 AM", ...]).
        Returns empty list if the date is not a working day.
    """
    # Check if the day is a working day (Mon=0 through Sat=5)
    if target_date.weekday() not in settings.working_days:
        return []

    slots = []
    current = datetime.combine(target_date, time(settings.opening_hour, 0))
    # Last slot must START before closing time
    end = datetime.combine(target_date, time(settings.closing_hour, 0))

    while current < end:
        slots.append(current.strftime("%-I:%M %p"))
        current += timedelta(minutes=settings.slot_duration_minutes)

    return slots


def is_working_day(target_date: date) -> bool:
    """Check if a date falls on a working day (Mon–Sat)."""
    return target_date.weekday() in settings.working_days


def is_within_working_hours(target_time: time) -> bool:
    """Check if a time falls within clinic working hours (9 AM – 6 PM)."""
    opening = time(settings.opening_hour, 0)
    closing = time(settings.closing_hour, 0)
    return opening <= target_time < closing


def is_future_date(target_date: date) -> bool:
    """Check if a date is today or in the future."""
    return target_date >= date.today()


def parse_date(date_str: str) -> Optional[date]:
    """
    Parse a date string in multiple formats.

    Supported formats:
        - 2026-07-05
        - 07/05/2026
        - July 5, 2026
        - Jul 5 2026

    Args:
        date_str: Date string to parse.

    Returns:
        Parsed date object or None if parsing fails.
    """
    formats = [
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%B %d, %Y",
        "%b %d %Y",
        "%B %d %Y",
        "%m-%d-%Y",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue

    return None


def parse_time(time_str: str) -> Optional[time]:
    """
    Parse a time string in multiple formats.

    Supported formats:
        - 10:00 AM / 10:00 am
        - 10:00AM
        - 10 AM
        - 14:00

    Args:
        time_str: Time string to parse.

    Returns:
        Parsed time object or None if parsing fails.
    """
    formats = [
        "%I:%M %p",
        "%I:%M%p",
        "%I %p",
        "%I%p",
        "%H:%M",
    ]

    cleaned = time_str.strip().upper()

    for fmt in formats:
        try:
            return datetime.strptime(cleaned, fmt).time()
        except ValueError:
            continue

    return None


def format_date_for_speech(target_date: date) -> str:
    """
    Format a date for natural speech output.

    Example: date(2026, 7, 5) -> "Saturday, July 5th"
    """
    day = target_date.day
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][day % 10 - 1]

    return target_date.strftime(f"%A, %B {day}{suffix}")


def format_time_for_speech(target_time: time) -> str:
    """
    Format a time for natural speech output.

    Example: time(10, 0) -> "10 AM"
    Example: time(14, 30) -> "2:30 PM"
    """
    if target_time.minute == 0:
        return target_time.strftime("%-I %p")
    return target_time.strftime("%-I:%M %p")


def generate_booking_id(target_date: date, sequence: int) -> str:
    """
    Generate a unique booking ID.

    Format: BK-YYYYMMDD-NNN
    Example: BK-20260705-003

    Args:
        target_date: Appointment date.
        sequence: Sequential number for that date.

    Returns:
        Formatted booking ID string.
    """
    return f"BK-{target_date.strftime('%Y%m%d')}-{sequence:03d}"
