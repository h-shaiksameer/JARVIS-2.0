from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable

from .models import CommandKind


@dataclass(frozen=True)
class CommandDefinition:
    command_id: str
    aliases: tuple[str, ...]
    handler: Callable[..., Any]
    kind: CommandKind = CommandKind.TOOL
    description: str = ""
    requires_confirmation: bool = False


class CommandRegistry:
    def __init__(self) -> None:
        self._definitions: dict[str, CommandDefinition] = {}
        self._aliases: dict[str, str] = {}

    @staticmethod
    def normalize(text: str) -> str:
        return " ".join(text.casefold().strip().split())

    def register(self, definition: CommandDefinition) -> None:
        self._definitions[definition.command_id] = definition
        for alias in (definition.command_id, *definition.aliases):
            self._aliases[self.normalize(alias)] = definition.command_id

    def register_many(self, definitions: Iterable[CommandDefinition]) -> None:
        for definition in definitions:
            self.register(definition)

    def get(self, command_id: str) -> CommandDefinition | None:
        return self._definitions.get(command_id)

    def resolve_exact(self, text: str) -> CommandDefinition | None:
        command_id = self._aliases.get(self.normalize(text))
        return self.get(command_id) if command_id else None

    def definitions(self) -> tuple[CommandDefinition, ...]:
        return tuple(self._definitions.values())
