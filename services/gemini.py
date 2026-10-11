from __future__ import annotations

import requests

from core.config import AppConfig
from core.result import ServiceResult


class GeminiService:
    def __init__(self, config: AppConfig, session: requests.Session | None = None) -> None:
        self.config = config
        self.session = session or requests.Session()

    def _url(self) -> str:
        return f"{self.config.gemini_endpoint}/models/{self.config.gemini_model}:generateContent"

    def generate(self, message: str) -> str:
        result = self.request(message)
        if not result.success:
            return result.message
        return str(result.data.get("text", ""))

    def request(self, message: str) -> ServiceResult:
        if not self.config.gemini_api_key:
            return ServiceResult.failure("AI service is not configured.", "missing_api_key")

        payload = {
            "contents": [{"parts": [{"text": message}]}],
            "generationConfig": {
                "temperature": self.config.gemini_temperature,
                "maxOutputTokens": self.config.gemini_max_output_tokens,
            },
        }
        try:
            response = self.session.post(
                self._url(),
                params={"key": self.config.gemini_api_key},
                json=payload,
                timeout=(self.config.gemini_connect_timeout, self.config.gemini_read_timeout),
            )
        except requests.RequestException:
            return ServiceResult.failure("AI service is temporarily unavailable.", "network_error", True)

        if response.status_code == 429:
            return ServiceResult.failure("AI service quota is temporarily exhausted.", "quota_exhausted", True)
        if response.status_code in {401, 403}:
            return ServiceResult.failure("AI service authentication failed.", "authentication_error")
        if response.status_code >= 500:
            return ServiceResult.failure("AI service is temporarily unavailable.", "provider_error", True)
        if not response.ok:
            return ServiceResult.failure("AI service rejected the request.", "provider_request_error")

        try:
            body = response.json()
            text = body["candidates"][0]["content"]["parts"][0]["text"]
        except (ValueError, KeyError, IndexError, TypeError):
            return ServiceResult.failure("AI service returned an invalid response.", "malformed_response")
        return ServiceResult.ok(data={"text": text})

    def check(self) -> ServiceResult:
        return self.request("Reply with exactly HEALTH_CHECK_OK")
