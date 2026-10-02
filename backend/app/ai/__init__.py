"""
AI Provider Package for CloudSentinel AI.

Defines the contract every LLM backend (OpenAI, Bedrock, Ollama) must
satisfy so explainability features work identically regardless of which
provider is configured. Explanations are generated from finding/attack
path context; responses are parsed downstream by `ai.parser`.

Phase 1 scaffold: interface + types only. Phase 3 wires the providers
with caching and retries (roadmap_part3_risk_ai_dashboard.md —
"Explainable AI Recommendations").
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


# --- Errors ----------------------------------------------------------------
class AIProviderError(Exception):
    """Base error for AI provider failures."""


class AIProviderUnavailable(AIProviderError):
    """Provider unreachable: missing credentials, network down, service off."""


class AIProviderResponseError(AIProviderError):
    """Provider responded but the output was empty or unparseable."""


# --- Request / response ----------------------------------------------------
@dataclass
class ExplanationRequest:
    """What to explain and for whom.

    `kind` is one of "finding", "attack_path", or "recommendation";
    `context` carries the raw facts (rule id, resource, path steps) the
    provider renders into human-readable text.
    """

    kind: str
    title: str
    context: dict[str, Any] = field(default_factory=dict)
    audience: str = "analyst"  # analyst | executive | developer
    max_tokens: int = 512


@dataclass
class Explanation:
    """Provider output plus provenance for auditability."""

    text: str
    provider: str
    model: str
    tokens_used: int = 0
    cached: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


# --- Provider contract -----------------------------------------------------
class BaseAIProvider(ABC):
    """Abstract LLM backend.

    Subclasses implement `explain()` (single-shot text generation) and
    `is_available()` (cheap capability probe used by the health endpoint
    and the scan pipeline's fallback logic).
    """

    name: str = "base"
    model: str = "unknown"

    @abstractmethod
    def explain(self, request: ExplanationRequest) -> Explanation:
        """Generate a human-readable explanation for the request."""
        raise NotImplementedError

    @abstractmethod
    def is_available(self) -> bool:
        """Return True when the provider can serve requests right now."""
        raise NotImplementedError

    def recommend(self, request: ExplanationRequest) -> list[str]:
        """Extract actionable recommendations from an explanation.

        Default implementation delegates to `explain()` and splits its
        text on recommendation markers; providers with structured
        outputs override this.
        """
        explanation = self.explain(request)
        lines = [
            line.lstrip("-•* ").strip()
            for line in explanation.text.splitlines()
            if line.strip().startswith(("-", "•", "*"))
        ]
        return lines or [explanation.text.strip()]


__all__ = [
    "AIProviderError",
    "AIProviderUnavailable",
    "AIProviderResponseError",
    "ExplanationRequest",
    "Explanation",
    "BaseAIProvider",
]
