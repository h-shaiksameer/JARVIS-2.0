from __future__ import annotations

from .command_registry import CommandRegistry
from .models import CommandContext, CommandKind, CommandMatch


class CommandRouter:
    """Resolve normalized commands without containing feature implementation logic."""

    def __init__(self, registry: CommandRegistry | None = None) -> None:
        self.registry = registry or CommandRegistry()

    def resolve(self, text: str) -> CommandMatch | None:
        normalized = self.registry.normalize(text)
        if not normalized:
            return None

        definition = self.registry.resolve_exact(normalized)
        if definition is None:
            candidates = []
            for item in self.registry.definitions():
                aliases = (item.command_id, *item.aliases)
                if any(self.registry.normalize(alias) in normalized for alias in aliases):
                    candidates.append(item)
            definition = candidates[0] if candidates else None

        if definition is None:
            return None

        return CommandMatch(
            command_id=definition.command_id,
            kind=definition.kind,
            handler=definition.handler,
            context=CommandContext(raw_text=text, normalized_text=normalized),
            requires_confirmation=definition.requires_confirmation,
        )
