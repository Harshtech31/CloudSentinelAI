"""
AWS Security Groups Collector.

Phase 1 stub: returns empty structured result without calling AWS.
Phase 2 (roadmap_part2_core_pipeline.md) adds real enumeration of
security groups and their ingress/egress rules per region.
"""

from typing import Any

from app.collectors.base import BaseCollector


class SecurityGroupCollector(BaseCollector):
    """Collects security groups and their rules from AWS regions."""

    provider = "aws"

    def collect(self) -> dict[str, list[dict[str, Any]]]:
        """Return empty SG resource sets (stub — real collection in Phase 2)."""
        self.record("security_groups", [])
        return self.resources
