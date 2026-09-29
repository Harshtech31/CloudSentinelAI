"""
Analyzer Base Classes for CloudSentinel AI.

Defines the contract every rule analyzer must implement so the
misconfiguration orchestrator can run any analyzer uniformly against
collected cloud resources.

Phase 1 scaffold: concrete rule sets (IAM, networking, storage,
encryption, compliance) arrive in Phase 2
(roadmap_part2_core_pipeline.md — "Real Collectors & Analyzers").
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from app.core.constants import Severity
from app.core.logging import logger


@dataclass
class RawFinding:
    """A single misconfiguration finding produced by an analyzer rule.

    Deliberately storage-agnostic: the scan pipeline maps this onto the
    `Finding` database model (Member 1 track) with rule_id, severity,
    resource identifiers, and remediation guidance intact.
    """

    rule_id: str
    title: str
    description: str
    severity: Severity
    resource_type: str
    resource_id: str
    resource_arn: str | None = None
    region: str | None = None
    remediation: str | None = None
    remediation_url: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class BaseAnalyzer(ABC):
    """Abstract base class for all security rule analyzers.

    Subclasses declare a `service` (matching collector resource keys)
    and implement `analyze()` to evaluate resource dictionaries against
    their rule set, returning `RawFinding` items.
    """

    service: str = "unknown"

    @abstractmethod
    def analyze(self, resources: dict[str, list[dict[str, Any]]]) -> list[RawFinding]:
        """Evaluate collected resources and return misconfiguration findings."""
        raise NotImplementedError

    def make_finding(self, **kwargs: Any) -> RawFinding:
        """Build a RawFinding with this analyzer's service context applied."""
        kwargs.setdefault("resource_type", self.service)
        finding = RawFinding(**kwargs)
        logger.debug(
            "Analyzer %s produced finding %s (%s)",
            self.__class__.__name__,
            finding.rule_id,
            finding.severity,
        )
        return finding
