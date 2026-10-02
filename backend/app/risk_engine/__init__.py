"""
Risk Engine Package for CloudSentinel AI.

Scores misconfiguration findings and attack paths with context-aware
weights (exposure, sensitivity, privilege), then prioritizes them so the
dashboard and reports surface the riskiest items first.

Phase 1 scaffold: base types and module seams only. The full weighted
formula, attack-path enrichment, and business-context calibration land
in Phase 3 (roadmap_part3_risk_ai_dashboard.md — "Context-Aware Risk
Scoring").
"""

from dataclasses import dataclass, field
from enum import StrEnum

from app.core.constants import Severity


class RiskBand(StrEnum):
    """Qualitative band a numeric risk score maps onto."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class RiskScore:
    """Outcome of scoring one finding or attack path.

    `score` is a 0-10 float (CVSS-style) so it can be displayed beside
    severity chips in the dashboard; `factors` records which weighted
    inputs drove the result for explainability.
    """

    score: float
    band: RiskBand
    factors: dict[str, float] = field(default_factory=dict)


class BaseScorer:
    """Base class for anything that turns a context into a RiskScore.

    Subclasses (the Phase 3 calculator) override `score()`; the base
    enforces the 0-10 contract and band mapping so callers can rely on
    consistent output ranges.
    """

    def score(self, context: object) -> RiskScore:  # pragma: no cover - stub
        raise NotImplementedError

    @staticmethod
    def clamp(score: float) -> float:
        """Constrain a raw score to the 0-10 display range."""
        return round(min(max(score, 0.0), 10.0), 1)


__all__ = ["RiskBand", "RiskScore", "BaseScorer", "Severity"]
