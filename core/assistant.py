from __future__ import annotations

from typing import Any, Optional

from .command_router import CommandRouter
from .config import AppConfig


class JarvisAssistant:
    """High-level orchestrator for the assistant runtime."""

    def __init__(self, router: Optional[CommandRouter] = None, config: Optional[AppConfig] = None) -> None:
        self.router = router or CommandRouter()
        self.config = config or AppConfig.from_environment()

    def register_default_commands(self) -> None:
        """Override in specialized subclasses for app-specific route registration."""

    def handle(self, command: str, *args: Any, **kwargs: Any) -> Any:
        handler = self.router.resolve(command)
        if handler is None:
            return "I did not understand that command."
        return handler(*args, **kwargs)

    def run(self) -> None:
        """Run the real assistant. This remains a compatibility entry point."""
        try:
            from myAI import main

            main()
        except Exception as exc:  # pragma: no cover - compatibility fallback
            print(f"Assistant startup failed in compatibility mode: {exc}")
            print("Use the modular runtime through jarvis_app.py when ready.")
