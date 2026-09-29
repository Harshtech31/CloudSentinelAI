"""
AWS Config Collector.

Phase 1 stub: returns empty structured result without calling AWS.
Phase 2 (roadmap_part2_core_pipeline.md) adds real enumeration of
AWS Config recorder status and delivery channels.
"""

from typing import Any

from app.collectors.base import BaseCollector


class AWSConfigCollector(BaseCollector):
    """Collects AWS Config recorder status from AWS regions."""

    provider = "aws"

    def collect(self) -> dict[str, list[dict[str, Any]]]:
        """Return empty Config resource sets (stub — real collection in Phase 2)."""
        self.record("config_recorders", [])
        return self.resources
