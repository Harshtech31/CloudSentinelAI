"""
AWS IAM Collector.

Phase 1 stub: returns empty structured result without calling AWS.
Phase 2 (roadmap_part2_core_pipeline.md) replaces this with real boto3
enumeration of users, roles, attached/inline policies, and MFA status.
"""

from typing import Any

from app.collectors.base import BaseCollector


class IAMCollector(BaseCollector):
    """Collects IAM users, roles, and policies from an AWS account."""

    provider = "aws"

    def collect(self) -> dict[str, list[dict[str, Any]]]:
        """Return empty IAM resource sets (stub — real collection in Phase 2)."""
        self.record("iam_users", [])
        self.record("iam_roles", [])
        self.record("iam_policies", [])
        return self.resources
