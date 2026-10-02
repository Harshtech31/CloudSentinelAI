"""
Risk Calculator for CloudSentinel AI.

Phase 1 stub of the context-aware formula:
    score = clamp(base_severity × exposure × sensitivity × privilege)
Attack-path enrichment and business-impact calibration arrive in
Phase 3 (roadmap_part3_risk_ai_dashboard.md).
"""

from typing import Any

from app.core.constants import Severity
from app.core.logging import logger
from app.risk_engine import BaseScorer, RiskBand, RiskScore
from app.risk_engine.context import Exposure, Privilege, RiskContext, Sensitivity
from app.risk_engine.weights import (
    RISK_BAND_THRESHOLDS,
    SEVERITY_BASE_SCORE,
    WEIGHT_EXPOSURE_INTERNAL,
    WEIGHT_EXPOSURE_PRIVATE,
    WEIGHT_EXPOSURE_PUBLIC,
    WEIGHT_PRIVILEGE_ADMIN,
    WEIGHT_PRIVILEGE_NONE,
    WEIGHT_PRIVILEGE_READ,
    WEIGHT_PRIVILEGE_WRITE,
    WEIGHT_SENSITIVITY_DEFAULT,
    WEIGHT_SENSITIVITY_DEVELOPMENT,
    WEIGHT_SENSITIVITY_PRODUCTION,
    WEIGHT_SENSITIVITY_SENSITIVE,
)

_EXPOSURE_WEIGHT = {
    Exposure.PUBLIC: WEIGHT_EXPOSURE_PUBLIC,
    Exposure.INTERNAL: WEIGHT_EXPOSURE_INTERNAL,
    Exposure.PRIVATE: WEIGHT_EXPOSURE_PRIVATE,
}

_SENSITIVITY_WEIGHT = {
    Sensitivity.SENSITIVE: WEIGHT_SENSITIVITY_SENSITIVE,
    Sensitivity.PRODUCTION: WEIGHT_SENSITIVITY_PRODUCTION,
    Sensitivity.DEFAULT: WEIGHT_SENSITIVITY_DEFAULT,
    Sensitivity.DEVELOPMENT: WEIGHT_SENSITIVITY_DEVELOPMENT,
}

_PRIVILEGE_WEIGHT = {
    Privilege.ADMIN: WEIGHT_PRIVILEGE_ADMIN,
    Privilege.WRITE: WEIGHT_PRIVILEGE_WRITE,
    Privilege.READ: WEIGHT_PRIVILEGE_READ,
    Privilege.NONE: WEIGHT_PRIVILEGE_NONE,
}


def band_for(score: float) -> RiskBand:
    """Map a 0-10 score onto a qualitative band via descending thresholds."""
    for threshold, band_name in RISK_BAND_THRESHOLDS:
        if score >= threshold:
            return RiskBand(band_name)
    return RiskBand.INFO


class RiskCalculator(BaseScorer):
    """Scores a finding in its resource context.

    The formula multiplies a severity anchor by three context
    multipliers, clamped to 0-10. `factors` records every input so the
    dashboard can show *why* a finding scored the way it did.
    """

    def score(self, context: Any) -> RiskScore:
        """Score one (severity, RiskContext) pair.

        `context` must expose `severity` (Severity) plus the
        RiskContext fields, or be a (severity, RiskContext) tuple.
        """
        severity, ctx = _unpack(context)
        exposure_w = _EXPOSURE_WEIGHT[ctx.exposure]
        sensitivity_w = _SENSITIVITY_WEIGHT[ctx.sensitivity]
        privilege_w = _PRIVILEGE_WEIGHT[ctx.privilege]

        raw = SEVERITY_BASE_SCORE[severity] * exposure_w * sensitivity_w * privilege_w
        score = self.clamp(raw)
        band = band_for(score)

        logger.debug(
            "Scored %s: base=%.2f exposure=%.2f sensitivity=%.2f privilege=%.2f -> %.1f (%s)",
            ctx.resource_id,
            SEVERITY_BASE_SCORE[severity],
            exposure_w,
            sensitivity_w,
            privilege_w,
            score,
            band,
        )
        return RiskScore(
            score=score,
            band=band,
            factors={
                "base": SEVERITY_BASE_SCORE[severity],
                "exposure": exposure_w,
                "sensitivity": sensitivity_w,
                "privilege": privilege_w,
                "guardrail_mfa": 1.0 if ctx.has_guardrail_mfa else 0.0,
                "guardrail_logging": 1.0 if ctx.has_guardrail_logging else 0.0,
            },
        )


def _unpack(context: Any) -> tuple[Severity, RiskContext]:
    """Accept (severity, RiskContext) tuple or an object with both."""
    if isinstance(context, tuple) and len(context) == 2:
        severity, ctx = context
        if isinstance(ctx, RiskContext):
            return severity, ctx
    for attr in ("severity",):
        if hasattr(context, attr) and hasattr(context, "exposure"):
            return context.severity, context  # type: ignore[arg-type]
    raise TypeError(
        f"RiskCalculator.score expects (Severity, RiskContext); got {type(context).__name__}"
    )


__all__ = ["RiskCalculator", "band_for"]
