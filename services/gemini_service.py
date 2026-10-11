from __future__ import annotations

from dataclasses import replace

from core.config import AppConfig
from services.gemini import GeminiService


DEFAULT_MODEL = "gemini-3.6-flash"


def get_gemini_api_key() -> str:
    return AppConfig.from_environment().gemini_api_key or ""


def generate_text(message: str, model_name: str = DEFAULT_MODEL) -> str:
    config = AppConfig.from_environment()
    if model_name:
        config = replace(config, gemini_model=model_name)
    service = GeminiService(config)
    return service.generate(message)
