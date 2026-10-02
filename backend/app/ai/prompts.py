"""
AI Prompt Templates for CloudSentinel AI.

Single place where LLM prompts are authored, so wording stays
consistent across providers and can be evaluated in the thesis. Phase 1
skeleton: the templates and their render function. Phase 3 tunes
wording against the evaluation scenarios
(roadmap_part3_risk_ai_dashboard.md).
"""

from string import Template
from typing import Any

# Audiences change vocabulary, not facts.
AUDIENCES: dict[str, str] = {
    "analyst": "a security analyst who needs technical specifics and remediation steps",
    "executive": "an executive who needs business impact in two sentences, no jargon",
    "developer": "the developer who owns the resource, with concrete config fixes",
}

SYSTEM_PROMPT = (
    "You are a cloud security expert on the CloudSentinel AI team. "
    "Explain findings factually using only the provided context. "
    "Never invent resources, rule ids, or severities. "
    "End with a short, actionable remediation list."
)

FINDING_PROMPT = Template(
    "Explain this cloud security finding for $audience.\n"
    "Rule: $rule_id — $title (severity: $severity)\n"
    "Resource: $resource_type $resource_id in $region\n"
    "What happened: $description\n"
    "Why it matters here: $risk_context\n"
    "Remediation: $remediation"
)

ATTACK_PATH_PROMPT = Template(
    "Explain this attack path for $audience.\n"
    "Path risk score: $score / 10 ($band)\n"
    "Steps: $steps\n"
    "Entry point: $entry\n"
    "Target: $target\n"
    "Weakest link: $weakest_link"
)

RECOMMENDATION_PROMPT = Template(
    "Given these findings for resource $resource_id, propose the three highest-value "
    "actions for $audience.\n"
    "Findings: $findings\n"
    "Rank by risk reduction per unit effort."
)


def _audience(name: str) -> str:
    """Resolve an audience key, falling back to analyst wording."""
    return AUDIENCES.get(name, AUDIENCES["analyst"])


def render_finding_prompt(context: dict[str, Any]) -> str:
    """Render the finding explanation prompt from context facts."""
    return FINDING_PROMPT.substitute(
        audience=_audience(str(context.get("audience", "analyst"))),
        rule_id=context.get("rule_id", "unknown"),
        title=context.get("title", "Untitled finding"),
        severity=context.get("severity", "unknown"),
        resource_type=context.get("resource_type", "resource"),
        resource_id=context.get("resource_id", "unknown"),
        region=context.get("region", "unknown region"),
        description=context.get("description", "No description provided."),
        risk_context=context.get("risk_context", "Standard exposure and sensitivity."),
        remediation=context.get("remediation", "No remediation captured."),
    )


def render_attack_path_prompt(context: dict[str, Any]) -> str:
    """Render the attack path explanation prompt from context facts."""
    steps = context.get("steps", [])
    return ATTACK_PATH_PROMPT.substitute(
        audience=_audience(str(context.get("audience", "analyst"))),
        score=context.get("score", "?"),
        band=context.get("band", "unknown"),
        steps=" -> ".join(str(s) for s in steps) if steps else "unknown path",
        entry=context.get("entry", "unknown entry point"),
        target=context.get("target", "unknown target"),
        weakest_link=context.get("weakest_link", "not identified"),
    )


def render_recommendation_prompt(context: dict[str, Any]) -> str:
    """Render the recommendation prompt from context facts."""
    findings = context.get("findings", [])
    return RECOMMENDATION_PROMPT.substitute(
        audience=_audience(str(context.get("audience", "analyst"))),
        resource_id=context.get("resource_id", "unknown"),
        findings="; ".join(str(f) for f in findings) if findings else "no findings",
    )


RENDERERS = {
    "finding": render_finding_prompt,
    "attack_path": render_attack_path_prompt,
    "recommendation": render_recommendation_prompt,
}


def render_prompt(kind: str, context: dict[str, Any]) -> str:
    """Render the prompt for a request kind; raises on unknown kinds."""
    renderer = RENDERERS.get(kind)
    if renderer is None:
        raise ValueError(f"Unknown explanation kind: {kind!r}")
    return renderer(context)


__all__ = [
    "AUDIENCES",
    "SYSTEM_PROMPT",
    "FINDING_PROMPT",
    "ATTACK_PATH_PROMPT",
    "RECOMMENDATION_PROMPT",
    "render_prompt",
    "render_finding_prompt",
    "render_attack_path_prompt",
    "render_recommendation_prompt",
]
