from __future__ import annotations

import re
from collections import defaultdict
from typing import Any, Callable, Iterable, Optional


class CommandRouter:
    """Simple, extensible route registry for assistant intents."""

    def __init__(self) -> None:
        self.routes: dict[str, list[Callable[..., Any]]] = defaultdict(list)

    @staticmethod
    def normalize(text: str) -> str:
        return re.sub(r"[^a-z0-9\s]", "", text.lower()).strip()

    def register(self, commands: Iterable[str], handler: Callable[..., Any]) -> None:
        for command in commands:
            normalized = self.normalize(command)
            self.routes[normalized].append(handler)

    def resolve(self, text: str) -> Optional[Callable[..., Any]]:
        normalized = self.normalize(text)

        if not normalized:
            return None

        if normalized in self.routes:
            return self.routes[normalized][0]

        for route in self.routes:
            if route in normalized or normalized in route:
                return self.routes[route][0]

        return None

    def execute(self, text: str, *args: Any, **kwargs: Any) -> Any:
        handler = self.resolve(text)
        if handler is None:
            raise ValueError(f"No handler registered for command: {text!r}")
        return handler(*args, **kwargs)
