"""
Explain Facade for CloudSentinel AI.

One entry point for the rest of the application: `explain_finding()` and
`explain_attack_path()` pick the first available provider (Bedrock, OpenAI, Ollama),
generate prompts, extract actionable remediation steps, and degrade gracefully to
deterministic static guidance when no LLM is reachable.
"""

from typing import Any

from app.ai import (
    AIProviderError,
    BaseAIProvider,
    Explanation,
    ExplanationRequest,
)
from app.core.logging import logger

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


def get_default_providers() -> list[BaseAIProvider]:
    """Discover and return configured, active AI providers in priority order."""
    active: list[BaseAIProvider] = []

    # 1. Amazon Bedrock (Primary: Claude Haiku 4.5 / Nova)
    try:
        from app.ai.providers.bedrock import BedrockProvider

        bedrock = BedrockProvider()
        if bedrock.is_available():
            active.append(bedrock)
    except Exception as exc:
        logger.debug("BedrockProvider initialization skipped: %s", exc)

    # 2. Anthropic (Direct)
    try:
        from app.ai.providers.anthropic import AnthropicProvider

        anthropic_p = AnthropicProvider()
        if anthropic_p.is_available():
            active.append(anthropic_p)
    except Exception as exc:
        logger.debug("AnthropicProvider initialization skipped: %s", exc)

    # 3. OpenAI
    try:
        from app.ai.providers.openai import OpenAIProvider

        openai_p = OpenAIProvider()
        if openai_p.is_available():
            active.append(openai_p)
    except Exception as exc:
        logger.debug("OpenAIProvider initialization skipped: %s", exc)

    # 4. Ollama (local)
    try:
        from app.ai.providers.ollama import OllamaProvider

        ollama_p = OllamaProvider()
        if ollama_p.is_available():
            active.append(ollama_p)
    except Exception as exc:
        logger.debug("OllamaProvider initialization skipped: %s", exc)

    return active


def get_user_providers(integration: Any) -> list[BaseAIProvider]:
    """Build providers based on user's active integration preference."""
    if not integration:
        return get_default_providers()

    choice = getattr(integration, "ai_provider", "bedrock").lower()
    providers: list[BaseAIProvider] = []

    if choice == "openai" and getattr(integration, "openai_api_key", None):
        from app.ai.providers.openai import OpenAIProvider

        p = OpenAIProvider(
            api_key=integration.openai_api_key,
            model=getattr(integration, "openai_model", "gpt-4o-mini"),
        )
        if p.is_available():
            providers.append(p)
    elif choice == "anthropic" and getattr(integration, "anthropic_api_key", None):
        from app.ai.providers.anthropic import AnthropicProvider

        p = AnthropicProvider(
            api_key=integration.anthropic_api_key,
            model=getattr(integration, "anthropic_model", "claude-3-5-sonnet-20241022"),
        )
        if p.is_available():
            providers.append(p)
    elif choice == "bedrock":
        from app.ai.providers.bedrock import BedrockProvider

        p = BedrockProvider()
        if p.is_available():
            providers.append(p)

    # Append fallback default providers
    for default_p in get_default_providers():
        if default_p.name != choice:
            providers.append(default_p)

    return providers or get_default_providers()


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
    resolved_providers = providers if providers is not None else get_default_providers()
    last_error: AIProviderError | None = None

    for provider in resolved_providers:
        if not provider.is_available():
            logger.debug("Provider %s unavailable; skipping", provider.name)
            continue
        try:
            explanation = provider.explain(request)
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


__all__ = ["explain_finding", "explain_attack_path", "get_default_providers"]
