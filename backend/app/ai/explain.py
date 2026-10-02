"""
Explain Facade for CloudSentinel AI.

One entry point for the rest of the app: `explain_finding()` /
`explain_attack_path()` pick the first available provider, generate the
prompt, and degrade gracefully to static text when no LLM is reachable.

Phase 1 stub: facade + fallback behavior with provider selection logic
in place. Phase 3 adds response caching and token accounting
(roadmap_part3_risk_ai_dashboard.md).
"""

from typing import Any

from app.ai import (
    AIProviderError,
    BaseAIProvider,
    Explanation,
    ExplanationRequest,
)
from app.ai.prompts import render_prompt
from app.core.logging import logger

# Static fallback so the UI never shows an empty explanation card.
_FALLBACK_FINDING = (
    "No AI provider is configured. {title} ({rule_id}) was flagged {severity} "
    "on {resource_id}. Review the resource against the rule guidance and apply "
    "the documented remediation."
)
_FALLBACK_PATH = (
    "No AI provider is configured. This attack path reaches {target} through "
    "{hops} steps; the weakest link is {weakest_link}. Restrict the entry point "
    "and enforce guardrails on the flagged resources."
)


def explain_finding(
    finding: dict[str, Any],
    providers: list[BaseAIProvider] | None = None,
    audience: str = "analyst",
) -> Explanation:
    """Explain one finding dict (RawFinding-shaped) via the first working provider."""
    request = ExplanationRequest(
        kind="finding",
        title=str(finding.get("title", "Finding")),
        context={**finding, "audience": audience},
        audience=audience,
    )
    return _explain_with_fallback(request, finding, providers)


def explain_attack_path(
    path: dict[str, Any],
    providers: list[BaseAIProvider] | None = None,
    audience: str = "analyst",
) -> Explanation:
    """Explain one attack path dict via the first working provider."""
    request = ExplanationRequest(
        kind="attack_path",
        title=str(path.get("title", "Attack path")),
        context={**path, "audience": audience},
        audience=audience,
    )
    return _explain_with_fallback(request, path, providers)


def _explain_with_fallback(
    request: ExplanationRequest,
    facts: dict[str, Any],
    providers: list[BaseAIProvider] | None,
) -> Explanation:
    """Try each provider in order; fall back to static text."""
    last_error: AIProviderError | None = None
    for provider in providers or []:
        if not provider.is_available():
            logger.debug("Provider %s unavailable; skipping", provider.name)
            continue
        try:
            explanation = provider.explain(request)
            explanation.text = (
                render_prompt(request.kind, request.context) + "\n\n" + explanation.text
            )
            return explanation
        except AIProviderError as exc:
            last_error = exc
            logger.warning("Provider %s failed: %s", provider.name, exc)
    return _static_fallback(request, facts, last_error)


def _static_fallback(
    request: ExplanationRequest,
    facts: dict[str, Any],
    provider_error: AIProviderError | None = None,
) -> Explanation:
    """Deterministic fallback text built from the request facts."""
    if request.kind == "attack_path":
        text = _FALLBACK_PATH.format(
            target=facts.get("target", "sensitive data"),
            hops=facts.get("hops", "several"),
            weakest_link=facts.get("weakest_link", "an unhardened resource"),
        )
    else:
        text = _FALLBACK_FINDING.format(
            title=request.title,
            rule_id=facts.get("rule_id", "unknown rule"),
            severity=facts.get("severity", "unknown"),
            resource_id=facts.get("resource_id", "unknown resource"),
        )
    return Explanation(
        text=text,
        provider="fallback",
        model="none",
        metadata={
            "fallback": True,
            "provider_error": str(provider_error) if provider_error else None,
        },
    )


__all__ = ["explain_finding", "explain_attack_path"]
