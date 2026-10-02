"""
OpenAI Provider for CloudSentinel AI.

Phase 1 stub: lazy client construction and availability probing only —
no network calls at import time, no API key required to import. Phase 3
adds prompt assembly, response caching, and retries
(roadmap_part3_risk_ai_dashboard.md).
"""

from typing import Any

from app.ai import (
    AIProviderUnavailable,
    BaseAIProvider,
    Explanation,
    ExplanationRequest,
)
from app.core.config import settings
from app.core.logging import logger


class OpenAIProvider(BaseAIProvider):
    """OpenAI-backed explanation provider (stub)."""

    name = "openai"
    model: str = "gpt-4o-mini"

    def __init__(self) -> None:
        self._client: Any = None

    def _get_client(self) -> Any:
        """Build the OpenAI client lazily; raise when unconfigured."""
        if self._client is not None:
            return self._client
        api_key = getattr(settings, "OPENAI_API_KEY", None)
        if not api_key:
            raise AIProviderUnavailable("OPENAI_API_KEY is not configured")
        try:
            from openai import OpenAI  # imported lazily: optional dependency

            self._client = OpenAI(api_key=api_key)
        except ImportError as exc:
            raise AIProviderUnavailable("openai package not installed") from exc
        logger.debug("OpenAI client initialized (model=%s)", self.model)
        return self._client

    def is_available(self) -> bool:
        """True when an API key is configured; no network I/O."""
        return bool(getattr(settings, "OPENAI_API_KEY", None))

    def explain(self, request: ExplanationRequest) -> Explanation:
        """Generate an explanation via the OpenAI chat API (stub).

        Phase 1 raises rather than making network calls; Phase 3
        implements the real chat.completions round-trip.
        """
        client = self._get_client()
        logger.info(
            "OpenAI explain request (kind=%s, title=%s) via %s",
            request.kind,
            request.title,
            self.model,
        )
        raise AIProviderUnavailable(
            "OpenAI explanation generation lands in Phase 3; client is configured"
            f" and ready ({type(client).__name__})"
        )


__all__ = ["OpenAIProvider"]
