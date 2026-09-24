from pathlib import Path
import os


ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"


def test_env_file_is_valid_utf8_text():
    raw = ENV_PATH.read_bytes()
    assert raw, "The .env file must exist and not be empty."
    if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
        raw = raw.decode("utf-16").encode("utf-8")
    text = raw.decode("utf-8")
    assert "API_KEY=" in text or "GEMINI_API_KEY=" in text
    assert "OPENWEATHER_API_KEY=" in text
    assert "NEWS_API_KEY=" in text


def test_supported_gemini_model_name():
    supported = {"gemini-3.6-flash", "gemini-3.8-flash", "gemini-2.5-flash"}
    assert "gemini-3.6-flash" in supported


def test_google_genai_package_exists():
    import importlib.util

    assert importlib.util.find_spec("google.genai") is not None
