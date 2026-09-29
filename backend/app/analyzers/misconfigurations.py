"""
Misconfiguration Analysis Orchestrator.

Fans collected cloud resources out to every registered analyzer and
merges their findings. Phase 1 stub: analyzers are wired but all rule
sets are empty skeletons. Phase 2 (roadmap_part2_core_pipeline.md
task 25) turns this into the full rule router once real analyzers land.
"""

from typing import Any

from app.analyzers import BaseAnalyzer, RawFinding
from app.analyzers.compliance import ComplianceAnalyzer
from app.analyzers.encryption import EncryptionAnalyzer
from app.analyzers.iam import IAMAnalyzer
from app.analyzers.networking import NetworkingAnalyzer
from app.analyzers.storage import StorageAnalyzer
from app.core.logging import logger


class MisconfigurationOrchestrator:
    """Runs all analyzers over collected resources and merges findings."""

    def __init__(self, analyzers: list[BaseAnalyzer] | None = None) -> None:
        self.analyzers = analyzers or [
            IAMAnalyzer(),
            NetworkingAnalyzer(),
            StorageAnalyzer(),
            EncryptionAnalyzer(),
            ComplianceAnalyzer(),
        ]

    def run(self, resources: dict[str, list[dict[str, Any]]]) -> list[RawFinding]:
        """Run every analyzer and return merged, order-stable findings."""
        findings: list[RawFinding] = []
        for analyzer in self.analyzers:
            try:
                produced = analyzer.analyze(resources)
            except Exception as exc:  # noqa: BLE001 - one analyzer must not kill the scan
                logger.warning("Analyzer %s failed: %s", analyzer.__class__.__name__, exc)
                continue
            findings.extend(produced)
            logger.info(
                "Analyzer %s produced %d finding(s)",
                analyzer.__class__.__name__,
                len(produced),
            )
        return findings
