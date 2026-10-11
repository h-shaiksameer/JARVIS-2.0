from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Mapping


class AssistantState(str, Enum):
    STOPPED = "stopped"
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    ERROR = "error"


class CommandKind(str, Enum):
    TOOL = "tool"
    AI = "ai"
    LIFECYCLE = "lifecycle"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class CommandContext:
    raw_text: str
    normalized_text: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CommandMatch:
    command_id: str
    kind: CommandKind
    handler: Callable[..., Any]
    context: CommandContext
    requires_confirmation: bool = False


@dataclass(frozen=True)
class CommandResult:
    success: bool
    message: str
    command_id: str | None = None
    data: Mapping[str, Any] = field(default_factory=dict)
    error_code: str | None = None


@dataclass(frozen=True)
class AssistantResponse:
    text: str
    spoken: bool = False
    source: str = "assistant"
    command_id: str | None = None


@dataclass
class ApplicationState:
    state: AssistantState = AssistantState.STOPPED
    last_input: str = ""
    last_response: str = ""
    last_error: str | None = None
