from __future__ import annotations

import os
from typing import Any

try:
    from google import genai
except Exception:  # pragma: no cover - compatibility for missing SDK
    genai = None


DEFAULT_MODEL = "gemini-3.6-flash"


def get_gemini_api_key() -> str:
    return os.getenv("API_KEY") or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY") or ""


def get_gemini_client() -> Any:
    if genai is None:
        raise RuntimeError("google-genai is not installed. Install it with: pip install google-genai")
    api_key = get_gemini_api_key()
    if not api_key:
        raise RuntimeError("Gemini API key is missing. Set API_KEY or GOOGLE_API_KEY in the environment.")
    return genai.Client(api_key=api_key)


def generate_text(message: str, model_name: str = DEFAULT_MODEL) -> str:
    client = get_gemini_client()
    response = client.models.generate_content(model=model_name, contents=message)
    return getattr(response, "text", "") or ""
