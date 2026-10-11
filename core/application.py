from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .command_router import CommandRouter
from .models import ApplicationState, AssistantResponse, CommandKind


@dataclass
class AssistantApplication:
    router: CommandRouter
    ai_service: Any | None = None
    state: ApplicationState = field(default_factory=ApplicationState)

    def handle_text(self, text: str) -> AssistantResponse:
        self.state.last_input = text
        match = self.router.resolve(text)
        if match is not None:
            try:
                result = match.handler(match.context)
                message = getattr(result, "message", result)
                response = AssistantResponse(str(message), command_id=match.command_id)
            except Exception as exc:
                self.state.last_error = str(exc)
                response = AssistantResponse("That command could not be completed.", command_id=match.command_id)
        elif self.ai_service is not None:
            response = AssistantResponse(self.ai_service.generate(text), source="ai")
        else:
            response = AssistantResponse("I do not have an AI service configured.", source="ai")

        self.state.last_response = response.text
        return response

    def health(self) -> dict[str, Any]:
        return {
            "state": self.state.state.value,
            "last_input": self.state.last_input,
            "last_response": self.state.last_response,
            "last_error": self.state.last_error,
            "ai_configured": self.ai_service is not None,
        }
