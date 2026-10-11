from core.config import AppConfig


def test_config_uses_compatibility_key_order(monkeypatch):
    config = AppConfig(project_root='.', gemini_api_key='gemini-key')
    assert config.gemini_api_key == 'gemini-key'
    assert config.gemini_model
