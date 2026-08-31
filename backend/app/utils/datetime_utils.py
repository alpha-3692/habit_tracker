from datetime import date, datetime
from typing import Optional
import pytz


def get_user_today(timezone_str: Optional[str] = "UTC") -> date:
    """
    Returns today's date in the user's configured timezone.
    Falls back to UTC if timezone_str is invalid or missing.
    """
    if not timezone_str:
        timezone_str = "UTC"
    try:
        tz = pytz.timezone(timezone_str)
    except pytz.UnknownTimeZoneError:
        tz = pytz.UTC

    return datetime.now(tz).date()


def is_future_date(target_date: date, user_timezone: str = "UTC") -> bool:
    """Checks if a given date is in the future relative to the user's timezone."""
    today = get_user_today(user_timezone)
    return target_date > today
