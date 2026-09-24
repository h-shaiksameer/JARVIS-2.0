"""External service adapters for the assistant."""

from .system_service import (
    check_battery_status,
    open_chrome,
    open_cmd,
    open_github,
    open_instagram,
    open_linkedin,
    open_powerpoint,
    tell_time,
    get_weather,
)

__all__ = [
    "check_battery_status",
    "open_chrome",
    "open_cmd",
    "open_github",
    "open_instagram",
    "open_linkedin",
    "open_powerpoint",
    "tell_time",
    "get_weather",
]
