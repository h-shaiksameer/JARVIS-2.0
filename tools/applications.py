from __future__ import annotations

import subprocess
import webbrowser
from pathlib import Path
from typing import Mapping

from core.result import ServiceResult


class ApplicationTool:
    """Launch only configured applications and URLs; never execute raw user input."""

    def __init__(self, applications: Mapping[str, str | Path] | None = None, urls: Mapping[str, str] | None = None) -> None:
        self.applications = dict(applications or {})
        self.urls = dict(urls or {})

    def open(self, name: str) -> ServiceResult:
        key = name.casefold().strip()
        target = self.applications.get(key)
        if target is None:
            target = self.urls.get(key)
            if target is None:
                return ServiceResult.failure(f"Application '{name}' is not configured.", "unknown_application")
            webbrowser.open(target)
            return ServiceResult.ok(f"Opening {name}.")

        path = Path(target)
        if not path.exists():
            return ServiceResult.failure(f"Application '{name}' is unavailable on this computer.", "application_unavailable")
        subprocess.Popen([str(path)])
        return ServiceResult.ok(f"Opening {name}.")
