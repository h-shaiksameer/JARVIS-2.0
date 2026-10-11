from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


@dataclass
class AppConfig:
    project_root: str
    temp_dir: str = ""
    media_dir: str = ""
    response_dir: str = ""
    voice_dir: str = ""
    gemini_api_key: Optional[str] = None
    email_app_password: Optional[str] = None
    openweather_api_key: Optional[str] = None
    news_api_key: Optional[str] = None
    email: Optional[str] = None
    gemini_model: str = "gemini-3.6-flash"
    gemini_temperature: float = 0.2
    gemini_connect_timeout: float = 3.0
    gemini_read_timeout: float = 12.0
    gemini_max_output_tokens: int = 120

    @property
    def api_key(self) -> Optional[str]:
        return self.gemini_api_key

    @property
    def gemini_endpoint(self) -> str:
        return "https://generativelanguage.googleapis.com/v1beta"

    def path(self, *parts: str) -> Path:
        return Path(self.project_root, *parts)

    @classmethod
    def from_environment(cls) -> "AppConfig":
        root = Path(__file__).resolve().parents[1]
        load_dotenv(root / ".env", override=True)
        return cls(
            project_root=str(root),
            temp_dir=str(root / "temp"),
            media_dir=str(root / "media"),
            response_dir=str(root / "JarvisResponse"),
            voice_dir=str(root / "MyVoice"),
            gemini_api_key=os.getenv("API_KEY") or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"),
            email_app_password=os.getenv("EMAIL_APP_PASSWORD"),
            openweather_api_key=os.getenv("OPENWEATHER_API_KEY"),
            news_api_key=os.getenv("NEWS_API_KEY"),
            email=os.getenv("EMAIL"),
            gemini_model=os.getenv("GEMINI_MODEL", "gemini-3.6-flash"),
            gemini_temperature=float(os.getenv("GEMINI_TEMPERATURE", "0.2")),
            gemini_connect_timeout=float(os.getenv("GEMINI_CONNECT_TIMEOUT", "3")),
            gemini_read_timeout=float(os.getenv("GEMINI_READ_TIMEOUT", "12")),
            gemini_max_output_tokens=int(os.getenv("GEMINI_MAX_OUTPUT_TOKENS", "120")),
        )


def get_absolute_path(relative_path: str) -> str:
    return str(Path(AppConfig.from_environment().project_root) / relative_path)
