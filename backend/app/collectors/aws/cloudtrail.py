"""
AWS CloudTrail Collector.

Phase 1 stub: returns empty structured result without calling AWS.
Phase 2 (roadmap_part2_core_pipeline.md) adds real enumeration of
trails, their status, and logging configuration.
"""

from typing import Any

from app.collectors.base import BaseCollector


class CloudTrailCollector(BaseCollector):
    """Collects CloudTrail trails and logging status from AWS regions."""

    provider = "aws"

    def collect(self) -> dict[str, list[dict[str, Any]]]:
        """Return empty CloudTrail resource sets (stub — real collection in Phase 2)."""
        self.record("cloudtrail_trails", [])
        return self.resources
