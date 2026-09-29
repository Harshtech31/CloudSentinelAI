"""
IAM Security Rule Analyzer.

Phase 1 stub: rule methods exist as skeletons returning no findings.
Phase 2 (roadmap_part2_core_pipeline.md tasks 15-17) implements:
- root account MFA disabled            → CIS 1.5 / 1.6
- admin wildcard policy (`Action: "*"`)
- unused IAM credentials (> 90 days)
"""

from typing import Any

from app.analyzers import BaseAnalyzer, RawFinding


class IAMAnalyzer(BaseAnalyzer):
    """Evaluates IAM users, roles, and policies against security rules."""

    service = "iam"

    def analyze(self, resources: dict[str, list[dict[str, Any]]]) -> list[RawFinding]:
        """Run all IAM rules over collected IAM resources (stub — no findings yet)."""
        findings: list[RawFinding] = []
        findings.extend(self._check_root_mfa(resources))
        findings.extend(self._check_admin_wildcard_policy(resources))
        findings.extend(self._check_unused_credentials(resources))
        return findings

    def _check_root_mfa(self, resources: dict[str, list[dict[str, Any]]]) -> list[RawFinding]:
        """Rule AWS-IAM-001: root account MFA disabled (Phase 2)."""
        return []

    def _check_admin_wildcard_policy(
        self, resources: dict[str, list[dict[str, Any]]]
    ) -> list[RawFinding]:
        """Rule AWS-IAM-002: policy grants `Action: "*"` (Phase 2)."""
        return []

    def _check_unused_credentials(
        self, resources: dict[str, list[dict[str, Any]]]
    ) -> list[RawFinding]:
        """Rule AWS-IAM-003: credentials unused for 90+ days (Phase 2)."""
        return []
