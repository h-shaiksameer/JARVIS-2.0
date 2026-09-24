from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


@dataclass
class AppConfig:
    project_root: str
    api_key: Optional[str] = None
    email_app_password: Optional[str] = None
    openweather_api_key: Optional[str] = None
    news_api_key: Optional[str] = None
    email: Optional[str] = None

    @classmethod
    def from_environment(cls) -> "AppConfig":
        load_dotenv()
        root = Path(__file__).resolve().parents[1]
        return cls(
            project_root=str(root),
            api_key=os.getenv("API_KEY") or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"),
            email_app_password=os.getenv("EMAIL_APP_PASSWORD"),
            openweather_api_key=os.getenv("OPENWEATHER_API_KEY"),
            news_api_key=os.getenv("NEWS_API_KEY"),
            email=os.getenv("EMAIL"),
        )


def get_absolute_path(relative_path: str) -> str:
    return str(Path(AppConfig.from_environment().project_root) / relative_path)
