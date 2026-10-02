"""
Business Impact Mapper for CloudSentinel AI.

Bridges technical resources to business services so risk can be
expressed in business terms ("payment data at risk") rather than only
technical terms ("S3 bucket public").

Phase 1 stub: tag-driven mapping with sensible defaults. Phase 3 adds
the configurable service registry and graph-derived blast radius
(roadmap_part3_risk_ai_dashboard.md — business impact calibration).
"""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from app.core.logging import logger


class ImpactLevel(StrEnum):
    """Business impact if the resource is compromised."""

    SEVERE = "severe"
    MAJOR = "major"
    MODERATE = "moderate"
    MINOR = "minor"


# Tags that escalate impact when present (case-insensitive values).
_SEVERE_TAG_VALUES = {"pci", "pii", "phi", "payments", "financial", "hipaa"}
_MAJOR_TAG_VALUES = {"production", "prod", "customer", "core"}

# Resource types that are sensitive by their nature.
_SENSITIVE_TYPES = {"s3_bucket", "secrets_manager", "rds_instance", "dynamodb_table"}


@dataclass
class BusinessImpact:
    """Result of mapping a resource to its business context."""

    service: str
    level: ImpactLevel
    rationale: str
    owner: str | None = None
    revenue_critical: bool = False
    data_classes: list[str] = field(default_factory=list)


def map_impact(resource: dict[str, Any]) -> BusinessImpact:
    """Map one collected resource to its business impact.

    Precedence: explicit tags first (DataClass, Service, Owner), then
    environment tags, then resource-type defaults.
    """
    if not isinstance(resource, dict):
        resource = {}

    tags = {str(k).lower(): str(v).lower() for k, v in (resource.get("tags") or {}).items()}
    resource_type = str(resource.get("resource_type", "unknown"))
    resource_id = str(resource.get("resource_id", resource.get("name", "<unnamed>")))

    data_classes = [v for v in tags.values() if v in _SEVERE_TAG_VALUES]
    service = tags.get("service") or tags.get("application") or "unassigned"
    owner = tags.get("owner") or tags.get("team")

    if data_classes or resource.get("contains_secrets"):
        level, rationale = (
            ImpactLevel.SEVERE,
            f"Handles regulated or secret data ({', '.join(data_classes) or 'secrets'})",
        )
    elif (
        tags.get("environment", tags.get("env")) in _MAJOR_TAG_VALUES
        or resource_type in _SENSITIVE_TYPES
    ):
        level, rationale = (
            ImpactLevel.MAJOR,
            f"Production/sensitive resource type ({resource_type})",
        )
    elif tags.get("environment", tags.get("env")) in {"dev", "development", "sandbox", "test"}:
        level, rationale = ImpactLevel.MINOR, "Development environment"
    else:
        level, rationale = ImpactLevel.MODERATE, "Shared or unclassified resource"

    impact = BusinessImpact(
        service=service,
        level=level,
        rationale=rationale,
        owner=owner,
        revenue_critical=tags.get("revenue") in {"true", "1", "yes"},
        data_classes=sorted(set(data_classes)),
    )
    logger.debug("Mapped %s -> %s (%s)", resource_id, level, service)
    return impact


__all__ = ["ImpactLevel", "BusinessImpact", "map_impact"]
