"""Date formatting utilities."""

from datetime import date, datetime
from typing import Optional


def parse_date(date_str: Optional[str]) -> Optional[date]:
    """Parse an ISO date string to a date object."""
    if not date_str:
        return None
    try:
        # Handle both date and datetime strings
        if "T" in date_str:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00")).date()
        return date.fromisoformat(date_str[:10])
    except (ValueError, TypeError):
        return None


def format_date(date_str: Optional[str], include_year: bool = False) -> str:
    """Format a date string for display."""
    d = parse_date(date_str)
    if not d:
        return ""

    if include_year or d.year != date.today().year:
        return d.strftime("%b %d, %Y")
    return d.strftime("%b %d")


def format_relative_date(date_str: Optional[str]) -> str:
    """Format a date relative to today."""
    d = parse_date(date_str)
    if not d:
        return ""

    today = date.today()
    delta = (d - today).days

    if delta == 0:
        return "Today"
    elif delta == 1:
        return "Tomorrow"
    elif delta == -1:
        return "Yesterday"
    elif delta < -1:
        return f"{abs(delta)} days ago"
    elif delta <= 7:
        return d.strftime("%A")  # Day name
    else:
        return format_date(date_str)


def format_datetime(dt_str: Optional[str]) -> str:
    """Format a datetime string for display."""
    if not dt_str:
        return ""
    try:
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        return dt.strftime("%b %d, %Y %H:%M")
    except (ValueError, TypeError):
        return ""


def is_overdue(date_str: Optional[str]) -> bool:
    """Check if a date is in the past."""
    d = parse_date(date_str)
    if not d:
        return False
    return d < date.today()


def is_today(date_str: Optional[str]) -> bool:
    """Check if a date is today."""
    d = parse_date(date_str)
    if not d:
        return False
    return d == date.today()


def is_tomorrow(date_str: Optional[str]) -> bool:
    """Check if a date is tomorrow."""
    d = parse_date(date_str)
    if not d:
        return False
    tomorrow = date.today().replace(day=date.today().day + 1)
    return d == tomorrow
