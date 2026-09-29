"""
Storage Security Rule Analyzer.

Phase 1 stub: rule methods exist as skeletons returning no findings.
Phase 2 (roadmap_part2_core_pipeline.md tasks 20-21) implements:
- public S3 bucket (ACL grants + missing public access block)
- S3 bucket without versioning enabled
"""

from typing import Any

from app.analyzers import BaseAnalyzer, RawFinding


class StorageAnalyzer(BaseAnalyzer):
    """Evaluates S3 buckets against storage security rules."""

    service = "storage"

    def analyze(self, resources: dict[str, list[dict[str, Any]]]) -> list[RawFinding]:
        """Run all storage rules over collected resources (stub — no findings yet)."""
        findings: list[RawFinding] = []
        findings.extend(self._check_public_bucket(resources))
        findings.extend(self._check_versioning(resources))
        return findings

    def _check_public_bucket(self, resources: dict[str, list[dict[str, Any]]]) -> list[RawFinding]:
        """Rule AWS-S3-001: public S3 bucket (Phase 2)."""
        return []

    def _check_versioning(self, resources: dict[str, list[dict[str, Any]]]) -> list[RawFinding]:
        """Rule AWS-S3-002: bucket without versioning (Phase 2)."""
        return []
