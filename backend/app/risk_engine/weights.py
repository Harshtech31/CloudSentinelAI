"""
Risk Scoring Weights for CloudSentinel AI.

Single source of truth for every numeric weight the risk engine uses.
Kept as plain constants (not env config) so scores are reproducible and
defensible in the thesis evaluation; tuning happens via PR review, not
runtime knobs.

Phase 1 scaffold: the values below are the documented starting points
the Phase 3 calculator (roadmap_part3_risk_ai_dashboard.md) consumes.
"""

from app.core.constants import Severity

# --- Base score per finding severity (0-10, CVSS-style anchors) -----------
SEVERITY_BASE_SCORE: dict[Severity, float] = {
    Severity.CRITICAL: 9.5,
    Severity.HIGH: 7.5,
    Severity.MEDIUM: 5.0,
    Severity.LOW: 2.5,
    Severity.INFO: 0.5,
}

# --- Context multipliers (findings) ---------------------------------------
# score = base * exposure * sensitivity * privilege, clamped to 0-10.
WEIGHT_EXPOSURE_PUBLIC = 1.20  # internet-reachable resource
WEIGHT_EXPOSURE_INTERNAL = 1.00  # default: VPC-internal
WEIGHT_EXPOSURE_PRIVATE = 0.85  # no route from outside the VPC

WEIGHT_SENSITIVITY_SENSITIVE = 1.25  # holds secrets / PII / credentials
WEIGHT_SENSITIVITY_PRODUCTION = 1.10
WEIGHT_SENSITIVITY_DEFAULT = 1.00
WEIGHT_SENSITIVITY_DEVELOPMENT = 0.80

WEIGHT_PRIVILEGE_ADMIN = 1.30  # resource grants admin-level access
WEIGHT_PRIVILEGE_WRITE = 1.10
WEIGHT_PRIVILEGE_READ = 1.00
WEIGHT_PRIVILEGE_NONE = 0.90

# --- Attack path scoring --------------------------------------------------
# path_score = base(terminal severity) * hop_factor * guard_factor, clamped.
PATH_WEIGHT_HOP = 0.03  # each additional hop adds discovery complexity...
PATH_WEIGHT_HOP_DECAY = 0.95  # ...but each hop slightly reduces success odds
PATH_WEIGHT_INTERNET_ENTRY = 1.35  # starts from the internet
PATH_WEIGHT_CREDENTIAL_STEP = 1.15  # crosses a credential/role assumption
PATH_WEIGHT_DATA_TERMINUS = 1.30  # reaches sensitive data
PATH_WEIGHT_GUARDRAIL_MFA = 0.70  # an enforced guardrail damps the path
PATH_WEIGHT_GUARDRAIL_LOGGING = 0.85

# --- Dashboard aggregates -------------------------------------------------
# compliance_score = 100 * (passed / total), weighted by severity of rules.
COMPLIANCE_WEIGHT_BY_SEVERITY: dict[Severity, float] = {
    Severity.CRITICAL: 3.0,
    Severity.HIGH: 2.0,
    Severity.MEDIUM: 1.5,
    Severity.LOW: 1.0,
    Severity.INFO: 0.5,
}

# Band thresholds on the 0-10 scale (upper-bound inclusive).
RISK_BAND_THRESHOLDS: tuple[tuple[float, str], ...] = (
    (9.0, "critical"),
    (7.0, "high"),
    (4.0, "medium"),
    (1.5, "low"),
)


__all__ = [
    "SEVERITY_BASE_SCORE",
    "WEIGHT_EXPOSURE_PUBLIC",
    "WEIGHT_EXPOSURE_INTERNAL",
    "WEIGHT_EXPOSURE_PRIVATE",
    "WEIGHT_SENSITIVITY_SENSITIVE",
    "WEIGHT_SENSITIVITY_PRODUCTION",
    "WEIGHT_SENSITIVITY_DEFAULT",
    "WEIGHT_SENSITIVITY_DEVELOPMENT",
    "WEIGHT_PRIVILEGE_ADMIN",
    "WEIGHT_PRIVILEGE_WRITE",
    "WEIGHT_PRIVILEGE_READ",
    "WEIGHT_PRIVILEGE_NONE",
    "PATH_WEIGHT_HOP",
    "PATH_WEIGHT_HOP_DECAY",
    "PATH_WEIGHT_INTERNET_ENTRY",
    "PATH_WEIGHT_CREDENTIAL_STEP",
    "PATH_WEIGHT_DATA_TERMINUS",
    "PATH_WEIGHT_GUARDRAIL_MFA",
    "PATH_WEIGHT_GUARDRAIL_LOGGING",
    "COMPLIANCE_WEIGHT_BY_SEVERITY",
    "RISK_BAND_THRESHOLDS",
]
