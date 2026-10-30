"""
Direct Anthropic Provider for CloudSentinel AI.

Enables SOC analysts to connect their Anthropic Claude API keys directly (e.g. claude-3-5-sonnet)
without going through Amazon Bedrock.
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


class AnthropicProvider(BaseAIProvider):
    """Anthropic Messages API explanation provider."""

    name = "anthropic"

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or getattr(settings, "ANTHROPIC_API_KEY", "")
        self.model = model or getattr(settings, "ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")

    def is_available(self) -> bool:
        return bool(
            self.api_key and (self.api_key.startswith("sk-ant-") or len(self.api_key) >= 20)
        )

    def explain(self, request: ExplanationRequest) -> Explanation:
        if not self.is_available():
            raise AIProviderUnavailable("Anthropic API key is not configured or invalid")

        from app.ai.providers.bedrock import BedrockProvider

        prompt_text = BedrockProvider._build_prompt(None, request)

        payload = {
            "model": self.model,
            "max_tokens": 1500,
            "system": SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": prompt_text}],
            "temperature": 0.2,
        }

        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
                "User-Agent": "CloudSentinel-AI/1.0",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=25) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                raw_text = "".join(block.get("text", "") for block in data.get("content", []))
                tokens_used = data.get("usage", {}).get("output_tokens", 0) + data.get(
                    "usage", {}
                ).get("input_tokens", 0)
        except Exception as exc:
            logger.error("Anthropic invocation failed: %s", exc)
            raise AIProviderResponseError(f"Anthropic API call failed: {exc}") from exc

        if not raw_text.strip():
            raise AIProviderResponseError("Anthropic returned an empty response")

        recommendations = parse_recommendations(raw_text)
        return Explanation(
            text=raw_text,
            provider="anthropic",
            model=self.model,
            tokens_used=tokens_used,
            cached=False,
            metadata={"recommendations": recommendations},
        )


__all__ = ["AnthropicProvider"]
