from __future__ import annotations

from typing import Any

from core.command_router import CommandRouter


class DefaultAgent:
    """Registers the main assistant commands and executes them."""

    def __init__(self, router: CommandRouter) -> None:
        self.router = router

    def register_defaults(self) -> None:
        self.router.register(
            [
                "what is the time",
                "tell me time",
                "what time is it",
            ],
            self._time_command,
        )

        self.router.register(
            [
                "check weather",
                "open weather",
            ],
            self._weather_command,
        )

        self.router.register(
            [
                "open chrome",
                "launch chrome",
            ],
            self._chrome_command,
        )

    def _time_command(self, *args: Any, **kwargs: Any) -> str:
        from services.system_service import tell_time

        tell_time()
        return "Time check executed."

    def _weather_command(self, *args: Any, **kwargs: Any) -> str:
        from services.system_service import get_weather

        get_weather()
        return "Weather check executed."

    def _chrome_command(self, *args: Any, **kwargs: Any) -> str:
        from services.system_service import open_chrome

        open_chrome()
        return "Chrome launch requested."
