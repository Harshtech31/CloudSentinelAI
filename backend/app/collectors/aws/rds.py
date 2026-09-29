"""
AWS RDS Collector.

Phase 1 stub: returns empty structured result without calling AWS.
Phase 2 (roadmap_part2_core_pipeline.md) adds real enumeration of
DB instances with storage encryption and backup status.
"""

from typing import Any

from app.collectors.base import BaseCollector


class RDSCollector(BaseCollector):
    """Collects RDS instances and their security posture from AWS."""

    provider = "aws"

    def collect(self) -> dict[str, list[dict[str, Any]]]:
        """Return empty RDS resource sets (stub — real collection in Phase 2)."""
        self.record("rds_instances", [])
        return self.resources
