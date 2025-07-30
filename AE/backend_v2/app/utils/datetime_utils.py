from datetime import date, datetime, timedelta
from typing import List, Optional, Tuple, Union

import pytz

# Standard date/time formats
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
ISO_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
DISPLAY_FORMAT = "%b %d, %Y %H:%M:%S"
TIME_FORMAT = "%H:%M:%S"

# Trading hours time range for financial applications
MARKET_OPEN_TIME = "09:30:00"
MARKET_CLOSE_TIME = "16:00:00"


def get_current_datetime(timezone: str = "UTC") -> datetime:
    """
    Get the current datetime in the specified timezone.

    Args:
        timezone: Timezone name (default: UTC)

    Returns:
        Current datetime in the specified timezone
    """
    tz = pytz.timezone(timezone)
    return datetime.now(tz)


def convert_to_utc(dt: datetime) -> datetime:
    """
    Convert a datetime to UTC.

    Args:
        dt: Datetime to convert

    Returns:
        Datetime in UTC
    """
    if dt.tzinfo is None:
        # Assume naive datetime is in local timezone
        local_tz = pytz.timezone("UTC")
        dt = local_tz.localize(dt)

    return dt.astimezone(pytz.UTC)


def convert_from_utc(dt: datetime, timezone: str) -> datetime:
    """
    Convert a UTC datetime to another timezone.

    Args:
        dt: UTC datetime to convert
        timezone: Target timezone name

    Returns:
        Datetime in the specified timezone
    """
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        # Assume naive datetime is in UTC
        dt = pytz.UTC.localize(dt)

    target_tz = pytz.timezone(timezone)
    return dt.astimezone(target_tz)


def format_datetime(dt: datetime, format_str: str = DATETIME_FORMAT) -> str:
    """
    Format a datetime as a string.

    Args:
        dt: Datetime to format
        format_str: Format string (default: DATETIME_FORMAT)

    Returns:
        Formatted datetime string
    """
    return dt.strftime(format_str)


def parse_datetime(
    datetime_str: str, format_str: str = DATETIME_FORMAT, timezone: str = "UTC"
) -> datetime:
    """
    Parse a datetime string into a datetime object.

    Args:
        datetime_str: Datetime string to parse
        format_str: Format string (default: DATETIME_FORMAT)
        timezone: Timezone to set on the resulting datetime

    Returns:
        Parsed datetime object
    """
    dt = datetime.strptime(datetime_str, format_str)
    if timezone:
        tz = pytz.timezone(timezone)
        dt = tz.localize(dt)
    return dt


def is_trading_hours(
    dt: Optional[datetime] = None, timezone: str = "America/New_York"
) -> bool:
    """
    Check if the given datetime is within trading hours.

    Args:
        dt: Datetime to check (default: current time)
        timezone: Timezone for market hours (default: America/New_York for US markets)

    Returns:
        True if within trading hours, False otherwise
    """
    if dt is None:
        dt = get_current_datetime(timezone)
    else:
        dt = convert_from_utc(dt, timezone)

    # Check if it's a weekday (0 = Monday, 6 = Sunday)
    if dt.weekday() >= 5:  # Saturday or Sunday
        return False

    # Parse market open/close times
    open_time = datetime.strptime(MARKET_OPEN_TIME, TIME_FORMAT).time()
    close_time = datetime.strptime(MARKET_CLOSE_TIME, TIME_FORMAT).time()

    # Check if current time is within market hours
    current_time = dt.time()
    return open_time <= current_time <= close_time


def get_date_range(
    start_date: Union[date, datetime, str],
    end_date: Union[date, datetime, str],
    include_end: bool = True,
) -> List[date]:
    """
    Get a list of dates between start_date and end_date.

    Args:
        start_date: Start date
        end_date: End date
        include_end: Whether to include the end date (default: True)

    Returns:
        List of dates in the range
    """
    # Convert string dates to datetime objects if needed
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, DATE_FORMAT).date()
    elif isinstance(start_date, datetime):
        start_date = start_date.date()

    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, DATE_FORMAT).date()
    elif isinstance(end_date, datetime):
        end_date = end_date.date()

    # Calculate the delta
    delta = end_date - start_date
    if include_end:
        days = delta.days + 1
    else:
        days = delta.days

    # Generate date range
    return [(start_date + timedelta(days=i)) for i in range(days)]


def get_time_ago(dt: datetime) -> str:
    """
    Get a human-readable string representing how long ago the datetime was.

    Args:
        dt: Datetime to check

    Returns:
        String like "5 minutes ago", "2 hours ago", "3 days ago", etc.
    """
    now = datetime.now(pytz.UTC)
    if dt.tzinfo is None:
        dt = pytz.UTC.localize(dt)

    delta = now - dt
    seconds = delta.total_seconds()

    if seconds < 60:
        return "just now"
    if seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    if seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    if seconds < 604800:
        days = int(seconds / 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"
    if seconds < 2592000:
        weeks = int(seconds / 604800)
        return f"{weeks} week{'s' if weeks != 1 else ''} ago"
    if seconds < 31536000:
        months = int(seconds / 2592000)
        return f"{months} month{'s' if months != 1 else ''} ago"

    years = int(seconds / 31536000)
    return f"{years} year{'s' if years != 1 else ''} ago"


def quarter_start_end(year: int, quarter: int) -> Tuple[date, date]:
    """
    Get the start and end dates for a specific quarter.

    Args:
        year: Year
        quarter: Quarter (1-4)

    Returns:
        Tuple of (start_date, end_date)
    """
    if quarter < 1 or quarter > 4:
        raise ValueError("Quarter must be between 1 and 4")

    month = (quarter - 1) * 3 + 1

    start_date = date(year, month, 1)

    if quarter < 4:
        end_month = month + 3
        end_year = year
    else:
        end_month = 1
        end_year = year + 1

    end_date = date(end_year, end_month, 1) - timedelta(days=1)

    return start_date, end_date
