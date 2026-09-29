"""
AWS VPC Collector.

Phase 1 stub: returns empty structured result without calling AWS.
Phase 2 (roadmap_part2_core_pipeline.md) adds real enumeration of
VPCs, subnets, and route tables across regions.
"""

from typing import Any

from app.collectors.base import BaseCollector


class VPCCollector(BaseCollector):
    """Collects VPCs, subnets, and route tables from AWS regions."""

    provider = "aws"

    def collect(self) -> dict[str, list[dict[str, Any]]]:
        """Return empty VPC resource sets (stub — real collection in Phase 2)."""
        self.record("vpcs", [])
        self.record("subnets", [])
        self.record("route_tables", [])
        return self.resources
