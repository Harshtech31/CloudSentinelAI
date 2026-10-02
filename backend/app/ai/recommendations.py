"""
AI Recommendations for CloudSentinel AI.

Turns findings into a ranked, effort-aware action list — the data behind
the dashboard's "AI Recommendation Engine" row (thesis Figure 11.2).

Phase 1 stub: deterministic rule-based ranking (no LLM required), so
the recommendation cards render even without any provider. Phase 3
optionally enriches these with LLM re-ranking
(roadmap_part3_risk_ai_dashboard.md).
"""

from dataclasses import dataclass, field
from typing import Any

from app.core.constants import Severity
from app.core.logging import logger

# Risk-reduction scores (0-10) by finding severity — how much risk a
# remediated finding removes, anchored to the same scale the risk
# engine uses.
RISK_REDUCTION_BY_SEVERITY: dict[Severity, float] = {
    Severity.CRITICAL: 9.5,
    Severity.HIGH: 7.5,
    Severity.MEDIUM: 5.0,
    Severity.LOW: 2.5,
    Severity.INFO: 0.5,
}

# Relative effort per remediation keyword found in the remediation text.
_EFFORT_HINTS: dict[str, int] = {
    "enable": 1,
    "disable": 1,
    "rotate": 2,
    "update": 2,
    "attach": 2,
    "remove": 2,
    "restrict": 2,
    "create": 3,
    "migrate": 4,
    "redesign": 5,
}


@dataclass
class Recommendation:
    """One actionable item derived from a finding (or shared by several)."""

    title: str
    severity: Severity
    risk_reduction: float  # 0-10
    effort: int  # 1 (trivial) .. 5 (major project)
    findings: list[str] = field(default_factory=list)  # rule_ids covered
    resource_id: str | None = None

    @property
    def value_score(self) -> float:
        """Risk reduction per unit effort — the ranking key."""
        return round(self.risk_reduction / max(self.effort, 1), 2)


def _effort_for(remediation: str | None) -> int:
    """Estimate effort 1-5 from remediation wording (1 if no text)."""
    if not remediation:
        return 1
    text = remediation.lower()
    for keyword, effort in _EFFORT_HINTS.items():
        if keyword in text:
            return effort
    return 2


def recommend(findings: list[dict[str, Any]], top_n: int = 5) -> list[Recommendation]:
    """Build the top-N action list from RawFinding-shaped dicts.

    One recommendation per finding (Phase 1); Phase 3 clusters findings
    that share a remediation. Sorted by value_score desc, then severity.
    """
    recs: list[Recommendation] = []
    for finding in findings:
        if not isinstance(finding, dict):
            continue
        try:
            severity = Severity(str(finding.get("severity", Severity.MEDIUM)))
        except ValueError:
            severity = Severity.MEDIUM
        reduction = RISK_REDUCTION_BY_SEVERITY[severity]
        rec = Recommendation(
            title=str(finding.get("remediation") or finding.get("title") or "Review finding"),
            severity=severity,
            risk_reduction=reduction,
            effort=_effort_for(finding.get("remediation")),
            findings=[str(finding.get("rule_id", "unknown"))],
            resource_id=finding.get("resource_id"),
        )
        recs.append(rec)

    severity_order = {
        Severity.CRITICAL: 0,
        Severity.HIGH: 1,
        Severity.MEDIUM: 2,
        Severity.LOW: 3,
        Severity.INFO: 4,
    }
    recs.sort(key=lambda r: (-r.value_score, severity_order[r.severity], r.title))
    ranked = recs[:top_n]
    logger.info("Generated %d recommendations from %d findings", len(ranked), len(findings))
    return ranked


__all__ = ["Recommendation", "recommend", "RISK_REDUCTION_BY_SEVERITY"]
