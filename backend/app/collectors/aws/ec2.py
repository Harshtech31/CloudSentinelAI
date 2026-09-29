"""
AWS EC2 Collector.

Phase 1 stub: returns empty structured result without calling AWS.
Phase 2 (roadmap_part2_core_pipeline.md) adds real enumeration of
instances (with metadata and instance IAM profiles) across regions.
"""

from typing import Any

from app.collectors.base import BaseCollector


class EC2Collector(BaseCollector):
    """Collects EC2 instances and instance metadata from AWS regions."""

    provider = "aws"

    def collect(self) -> dict[str, list[dict[str, Any]]]:
        """Return empty EC2 resource sets (stub — real collection in Phase 2)."""
        self.record("ec2_instances", [])
        return self.resources
