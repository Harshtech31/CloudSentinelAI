"""
Encryption Security Rule Analyzer.

Phase 1 stub: rule methods exist as skeletons returning no findings.
Phase 2 (roadmap_part2_core_pipeline.md tasks 22-23) implements:
- unencrypted RDS instances
- unencrypted S3 buckets
"""

from typing import Any

from app.analyzers import BaseAnalyzer, RawFinding


class EncryptionAnalyzer(BaseAnalyzer):
    """Evaluates RDS/S3 storage encryption posture."""

    service = "encryption"

    def analyze(self, resources: dict[str, list[dict[str, Any]]]) -> list[RawFinding]:
        """Run all encryption rules over collected resources (stub — no findings yet)."""
        findings: list[RawFinding] = []
        findings.extend(self._check_unencrypted_rds(resources))
        findings.extend(self._check_unencrypted_s3(resources))
        return findings

    def _check_unencrypted_rds(
        self, resources: dict[str, list[dict[str, Any]]]
    ) -> list[RawFinding]:
        """Rule AWS-ENC-001: RDS storage unencrypted (Phase 2)."""
        return []

    def _check_unencrypted_s3(self, resources: dict[str, list[dict[str, Any]]]) -> list[RawFinding]:
        """Rule AWS-ENC-002: S3 bucket without default encryption (Phase 2)."""
        return []
