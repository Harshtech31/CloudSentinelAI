"""
Abstract Base Collector for CloudSentinel AI.

Defines the interface every cloud collector must implement so the scan
pipeline can run any provider (AWS/GCP/Azure) uniformly.

Phase 1 scaffold: real boto3 collection arrives in Phase 2
(roadmap_part2_core_pipeline.md — "Real Collectors & Analyzers").
"""

from abc import ABC, abstractmethod
from typing import Any

from app.core.logging import logger


class CollectorError(Exception):
    """Raised when a collector fails to gather data from a cloud provider."""


class CredentialsError(CollectorError):
    """Raised when cloud credentials are missing, invalid, or expired."""


class BaseCollector(ABC):
    """Abstract base class for all cloud resource collectors.

    Subclasses populate `self.resources` with lists of dicts keyed by
    service name (e.g. ``{"iam_users": [...], "ec2_instances": [...]}``).
    """

    provider: str = "unknown"

    def __init__(self, regions: list[str] | None = None) -> None:
        self.regions = regions or ["us-east-1"]
        self.resources: dict[str, list[dict[str, Any]]] = {}

    @abstractmethod
    def collect(self) -> dict[str, list[dict[str, Any]]]:
        """Collect all supported resources across configured regions."""
        raise NotImplementedError

    def collect_service(self, service: str) -> list[dict[str, Any]]:
        """Collect a single service's resources (default: run full collect)."""
        self.collect()
        return self.resources.get(service, [])

    def record(self, key: str, items: list[dict[str, Any]]) -> None:
        """Store collected items under a canonical resource key."""
        self.resources[key] = items
        logger.debug("Collected %d %s resource(s)", len(items), key)

    def summary(self) -> dict[str, int]:
        """Return per-service resource counts for scan reporting."""
        return {key: len(items) for key, items in self.resources.items()}
