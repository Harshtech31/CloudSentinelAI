"""
Ollama Provider for CloudSentinel AI.

Phase 1 stub: probes a local Ollama server without hard dependency on
the `ollama` package. Ideal for offline/air-gapped thesis demos — the
scan pipeline can fall back to it when OpenAI/Bedrock are unconfigured.
Phase 3 implements the real generation round-trip.
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


class OllamaProvider(BaseAIProvider):
    """Ollama-backed explanation provider (stub)."""

    name = "ollama"
    model: str = "llama3.2"

    def __init__(self, host: str | None = None) -> None:
        # settings.OLLAMA_HOST is optional; default to the conventional local port.
        self.host = host or getattr(settings, "OLLAMA_HOST", None) or "http://localhost:11434"
        self._client: Any = None

    def _get_client(self) -> Any:
        """Build the ollama client lazily; raise when unreachable."""
        if self._client is not None:
            return self._client
        try:
            import ollama  # optional dependency at this phase
        except ImportError as exc:
            raise AIProviderUnavailable("ollama package not installed") from exc
        try:
            self._client = ollama.Client(host=self.host)
        except Exception as exc:
            raise AIProviderUnavailable(f"Ollama client error: {exc}") from exc
        logger.debug("Ollama client initialized (host=%s)", self.host)
        return self._client

    def is_available(self) -> bool:
        """Cheap TCP probe of the Ollama server; never raises."""
        try:
            import socket
            from urllib.parse import urlparse

            parsed = urlparse(self.host)
            port = parsed.port or (443 if parsed.scheme == "https" else 80)
            with socket.create_connection((parsed.hostname, port), timeout=0.5):
                return True
        except OSError:
            return False

    def explain(self, request: ExplanationRequest) -> Explanation:
        """Generate an explanation via Ollama (stub; Phase 3 implements)."""
        self._get_client()
        raise AIProviderUnavailable("Ollama explanation generation lands in Phase 3")


__all__ = ["OllamaProvider"]
