from core.command_registry import CommandDefinition, CommandRegistry
from core.command_router import CommandRouter
from core.models import CommandKind
from core.result import ServiceResult


def test_registry_normalizes_aliases():
    registry = CommandRegistry()
    handler = lambda context: ServiceResult.ok("opened")
    registry.register(CommandDefinition("open_chrome", ("open chrome",), handler))
    assert registry.resolve_exact("  OPEN   CHROME ").command_id == "open_chrome"


def test_router_returns_structured_match():
    registry = CommandRegistry()
    registry.register(CommandDefinition("check_battery", ("battery status",), lambda context: "ok", CommandKind.TOOL))
    match = CommandRouter(registry).resolve("battery status")
    assert match is not None
    assert match.command_id == "check_battery"
    assert match.context.normalized_text == "battery status"
