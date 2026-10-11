from core.application import AssistantApplication
from core.command_registry import CommandDefinition, CommandRegistry
from core.command_router import CommandRouter
from core.result import ServiceResult


class FakeAI:
    def generate(self, message):
        return f"AI:{message}"

    def check(self):
        return ServiceResult.ok("ok")


def test_text_command_uses_registered_tool_before_ai():
    registry = CommandRegistry()
    registry.register(CommandDefinition("hello", ("hi",), lambda context: ServiceResult.ok("tool response")))
    app = AssistantApplication(CommandRouter(registry), FakeAI())
    assert app.handle_text("hi").text == "tool response"


def test_unknown_text_uses_ai():
    app = AssistantApplication(CommandRouter(), FakeAI())
    assert app.handle_text("what time is it").text == "AI:what time is it"
