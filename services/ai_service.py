from __future__ import annotations

from typing import Protocol

from core.result import ServiceResult


class AIService(Protocol):
    def generate(self, message: str) -> str:
        ...

    def check(self) -> ServiceResult:
        ...
