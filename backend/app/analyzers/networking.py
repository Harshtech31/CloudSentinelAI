"""
Networking Security Rule Analyzer.

Phase 1 stub: rule methods exist as skeletons returning no findings.
Phase 2 (roadmap_part2_core_pipeline.md tasks 18-19) implements:
- SG allows 0.0.0.0/0 on SSH (22) / RDP (3389)
- SG allows all traffic (all protocols, all sources)
"""

from typing import Any

from app.analyzers import BaseAnalyzer, RawFinding


class NetworkingAnalyzer(BaseAnalyzer):
    """Evaluates security groups and network topology against security rules."""

    service = "networking"

    def analyze(self, resources: dict[str, list[dict[str, Any]]]) -> list[RawFinding]:
        """Run all networking rules over collected resources (stub — no findings yet)."""
        findings: list[RawFinding] = []
        findings.extend(self._check_open_ssh_rdp(resources))
        findings.extend(self._check_all_traffic(resources))
        return findings

    def _check_open_ssh_rdp(self, resources: dict[str, list[dict[str, Any]]]) -> list[RawFinding]:
        """Rule AWS-NET-001: SG open to 0.0.0.0/0 on SSH/RDP (Phase 2)."""
        return []

    def _check_all_traffic(self, resources: dict[str, list[dict[str, Any]]]) -> list[RawFinding]:
        """Rule AWS-NET-002: SG allows all traffic from anywhere (Phase 2)."""
        return []
