from unittest.mock import Mock

from core.config import AppConfig
from services.gemini import GeminiService


def make_config():
    return AppConfig(project_root=".", gemini_api_key="test-key")


def test_gemini_429_is_structured():
    session = Mock()
    session.post.return_value.status_code = 429
    service = GeminiService(make_config(), session)
    result = service.request("hello")
    assert not result.success
    assert result.error_code == "quota_exhausted"
    assert result.retryable


def test_gemini_success_extracts_text():
    session = Mock()
    response = Mock(status_code=200, ok=True)
    response.json.return_value = {"candidates": [{"content": {"parts": [{"text": "hello"}]}}]}
    session.post.return_value = response
    result = GeminiService(make_config(), session).request("hello")
    assert result.success
    assert result.data["text"] == "hello"
