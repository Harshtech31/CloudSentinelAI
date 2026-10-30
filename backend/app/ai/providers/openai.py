"""
OpenAI Provider for CloudSentinel AI.

Generates root-cause analysis and remediation code via OpenAI models (e.g. gpt-4o, gpt-4o-mini).
"""

import json
import urllib.request

from app.ai import (
    AIProviderResponseError,
    AIProviderUnavailable,
    BaseAIProvider,
    Explanation,
    ExplanationRequest,
)
from app.ai.providers.bedrock import (
    SYSTEM_PROMPT,
    parse_recommendations,
)
from app.core.config import settings
from app.core.logging import logger


class OpenAIProvider(BaseAIProvider):
    """OpenAI-backed explanation provider."""

    name = "openai"

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or getattr(settings, "OPENAI_API_KEY", "")
        self.model = model or getattr(settings, "OPENAI_MODEL", "gpt-4o-mini")

    def is_available(self) -> bool:
        """True when an API key is configured."""
        return bool(self.api_key and (self.api_key.startswith("sk-") or len(self.api_key) >= 20))

    def explain(self, request: ExplanationRequest) -> Explanation:
        """Generate an explanation via OpenAI Chat Completions."""
        if not self.is_available():
            raise AIProviderUnavailable("OpenAI API key is not configured or invalid")

        from app.ai.providers.bedrock import BedrockProvider

        prompt_text = BedrockProvider._build_prompt(None, request)

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt_text},
            ],
            "temperature": 0.2,
            "max_tokens": 1500,
        }

        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "CloudSentinel-AI/1.0",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=25) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                choice = data.get("choices", [{}])[0]
                raw_text = choice.get("message", {}).get("content", "")
                tokens_used = data.get("usage", {}).get("total_tokens", 0)
        except Exception as exc:
            logger.error("OpenAI invocation failed: %s", exc)
            raise AIProviderResponseError(f"OpenAI API call failed: {exc}") from exc

        if not raw_text.strip():
            raise AIProviderResponseError("OpenAI returned an empty response")

        recommendations = parse_recommendations(raw_text)
        return Explanation(
            text=raw_text,
            provider="openai",
            model=self.model,
            tokens_used=tokens_used,
            cached=False,
            metadata={"recommendations": recommendations},
        )


__all__ = ["OpenAIProvider"]
