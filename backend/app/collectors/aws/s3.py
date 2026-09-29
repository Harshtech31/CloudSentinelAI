"""
AWS S3 Collector.

Phase 1 stub: returns empty structured result without calling AWS.
Phase 2 (roadmap_part2_core_pipeline.md) adds real enumeration of
buckets with ACL, public access block, encryption, and logging status.
"""

from typing import Any

from app.collectors.base import BaseCollector


class S3Collector(BaseCollector):
    """Collects S3 buckets and their security posture from AWS."""

    provider = "aws"

    def collect(self) -> dict[str, list[dict[str, Any]]]:
        """Return empty S3 resource sets (stub — real collection in Phase 2)."""
        self.record("s3_buckets", [])
        return self.resources
