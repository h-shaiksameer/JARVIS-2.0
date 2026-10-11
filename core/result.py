from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class ServiceResult:
    success: bool
    message: str = ""
    data: Mapping[str, Any] = field(default_factory=dict)
    error_code: str | None = None
    retryable: bool = False

    @classmethod
    def ok(cls, message: str = "", data: Mapping[str, Any] | None = None) -> "ServiceResult":
        return cls(True, message, data or {})

    @classmethod
    def failure(cls, message: str, error_code: str, retryable: bool = False) -> "ServiceResult":
        return cls(False, message, error_code=error_code, retryable=retryable)
