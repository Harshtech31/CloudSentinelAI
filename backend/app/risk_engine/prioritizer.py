"""
Risk Prioritizer for CloudSentinel AI.

Orders scored items so the highest-risk work surfaces first. Phase 1
stub: deterministic sort by (band, score, resource id). Phase 3 adds
attack-path enrichment and business-impact tiebreakers
(roadmap_part3_risk_ai_dashboard.md).
"""

from dataclasses import dataclass
from typing import Any

from app.core.logging import logger
from app.risk_engine import RiskBand, RiskScore

# Sorting order: CRITICAL first, INFO last.
_BAND_ORDER: dict[RiskBand, int] = {
    RiskBand.CRITICAL: 0,
    RiskBand.HIGH: 1,
    RiskBand.MEDIUM: 2,
    RiskBand.LOW: 3,
    RiskBand.INFO: 4,
}


@dataclass
class PrioritizedItem:
    """A scored item plus the context it was scored against."""

    label: str
    risk: RiskScore
    payload: Any = None


def prioritize(items: list[PrioritizedItem]) -> list[PrioritizedItem]:
    """Return items sorted worst-first.

    Tiebreaks: higher score wins, then alphabetical label for
    deterministic output (stable dashboards and reproducible tests).
    """
    ordered = sorted(
        items,
        key=lambda item: (_BAND_ORDER[item.risk.band], -item.risk.score, item.label),
    )
    logger.debug(
        "Prioritized %d items; top: %s", len(ordered), ordered[0].label if ordered else "n/a"
    )
    return ordered


__all__ = ["PrioritizedItem", "prioritize"]
