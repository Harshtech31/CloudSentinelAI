"""
Risk Context Data Model for CloudSentinel AI.

The context is everything the risk engine knows about a resource beyond
the finding itself: where it sits (exposure), what it touches
(sensitivity), what it can do (privilege), and whether guardrails
(MFA, logging) dampen exploitation.

Phase 1 scaffold: the model and its classifier helpers. Phase 3 wires
these classifiers to real graph data (roadmap_part3_risk_ai_dashboard.md,
"Context-Aware Risk Scoring").
"""

from dataclasses import dataclass, field
from enum import StrEnum

from app.core.constants import Severity


class Exposure(StrEnum):
    """How reachable a resource is from outside its VPC."""

    PUBLIC = "public"
    INTERNAL = "internal"
    PRIVATE = "private"


class Sensitivity(StrEnum):
    """How much damage a compromise of this resource causes."""

    SENSITIVE = "sensitive"
    PRODUCTION = "production"
    DEFAULT = "default"
    DEVELOPMENT = "development"


class Privilege(StrEnum):
    """Access level the resource (or an attacker through it) gains."""

    ADMIN = "admin"
    WRITE = "write"
    READ = "read"
    NONE = "none"


@dataclass
class RiskContext:
    """Context facts for one resource, fed to the risk calculator."""

    resource_id: str
    resource_type: str = "unknown"
    exposure: Exposure = Exposure.INTERNAL
    sensitivity: Sensitivity = Sensitivity.DEFAULT
    privilege: Privilege = Privilege.READ
    is_production: bool = False
    holds_secrets: bool = False
    has_guardrail_mfa: bool = False
    has_guardrail_logging: bool = False
    tags: dict[str, str] = field(default_factory=dict)


def classify_exposure(resource: dict) -> Exposure:
    """Classify exposure from collector output.

    Rules (Phase 1 defaults):
    - security groups with 0.0.0.0/0 ingress -> PUBLIC
    - resources flagged `public` (S3 public-read, RDS publicly_accessible)
      or attached to an internet gateway -> PUBLIC
    - resources with no network attachment at all -> PRIVATE
    - otherwise INTERNAL
    """
    if not isinstance(resource, dict):
        return Exposure.INTERNAL

    for sg in resource.get("security_groups", []) or []:
        for rule in sg.get("ip_permissions", []) or []:
            for block in rule.get("ip_ranges", []) or []:
                if block.get("cidr") in ("0.0.0.0/0", "::/0"):
                    return Exposure.PUBLIC
    if resource.get("public") or resource.get("publicly_accessible"):
        return Exposure.PUBLIC
    if resource.get("internet_gateway_id"):
        return Exposure.PUBLIC
    if resource.get("no_network") or resource.get("resource_type") in (
        "s3_bucket",
        "iam_user",
        "iam_role",
    ):
        return Exposure.PRIVATE
    return Exposure.INTERNAL


def classify_sensitivity(resource: dict) -> Sensitivity:
    """Classify sensitivity from naming, tags, and content hints."""
    if not isinstance(resource, dict):
        return Sensitivity.DEFAULT
    if resource.get("contains_secrets") or resource.get("holds_secrets"):
        return Sensitivity.SENSITIVE
    tags = resource.get("tags", {}) or {}
    env = str(tags.get("Environment", tags.get("env", ""))).lower()
    name = str(resource.get("name", resource.get("resource_id", ""))).lower()
    if "prod" in env or "prod" in name:
        return Sensitivity.PRODUCTION
    if env in ("dev", "development", "sandbox", "test"):
        return Sensitivity.DEVELOPMENT
    return Sensitivity.DEFAULT


def classify_privilege(resource: dict) -> Privilege:
    """Classify privilege level from attached IAM policy documents.

    A policy granting `Action: "*"` or `*:*` on `Resource: "*"` counts as
    ADMIN; any action whose name part (after the service prefix, e.g.
    `PutObject` in `s3:PutObject`) starts with a write verb is WRITE;
    service-scoped wildcards (`s3:*`) are WRITE; read-only actions are
    READ.
    """
    if not isinstance(resource, dict):
        return Privilege.READ
    actions: list[str] = []
    for doc in resource.get("policy_documents", []) or []:
        for stmt in doc.get("Statement", []) or []:
            if str(stmt.get("Effect", "Allow")).lower() != "allow":
                continue
            action = stmt.get("Action", [])
            actions.extend(action if isinstance(action, list) else [action])
    if any(a in ("*", "*:*") for a in actions):
        return Privilege.ADMIN
    write_verbs = ("write", "put", "create", "delete", "update", "attach", "modify")

    def is_write(action: str) -> bool:
        name = action.lower().split(":")[-1]  # 's3:PutObject' -> 'putobject'
        return name.startswith(write_verbs) or name == "*"

    if any(is_write(a) for a in actions):
        return Privilege.WRITE
    if actions:
        return Privilege.READ
    return Privilege.NONE


__all__ = [
    "Exposure",
    "Sensitivity",
    "Privilege",
    "RiskContext",
    "classify_exposure",
    "classify_sensitivity",
    "classify_privilege",
    "Severity",
]
