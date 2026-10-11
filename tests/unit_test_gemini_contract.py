from unittest.mock import Mock

import requests

from core.config import AppConfig
from services.gemini import GeminiService


def test_gemini_network_failure_is_graceful():
    session = Mock()
    session.post.side_effect = requests.ConnectionError("offline")
    result = GeminiService(AppConfig(project_root='.', gemini_api_key='key'), session).request('hello')
    assert result.success is False
    assert result.error_code == 'network_error'
    assert result.retryable is True
