"""
Background Task Package.

Hosts the scan orchestration task that chains
collectors → analyzers → risk → graph → persistence.
Phase 1 stub: defines the task skeleton and scan context only.
Phase 2 (roadmap_part2_core_pipeline.md task 4-5, Member 1 track)
implements the full pipeline wiring and DB persistence.
"""

from dataclasses import dataclass, field
from typing import Any

from app.core.constants import CloudProvider, ScanStatus
from app.core.logging import logger


@dataclass
class ScanContext:
    """Inputs for a single scan run, passed through every pipeline stage."""

    scan_id: str
    target_cloud: CloudProvider = CloudProvider.AWS
    regions: list[str] = field(default_factory=lambda: ["us-east-1"])
    services: list[str] = field(
        default_factory=lambda: ["iam", "ec2", "s3", "vpc", "security_groups", "rds", "cloudtrail"]
    )
    credentials: dict[str, str] = field(default_factory=dict)
    state: ScanStatus = ScanStatus.PENDING
    collected: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    findings: list[dict[str, Any]] = field(default_factory=list)


def run_scan_task(context: ScanContext) -> ScanContext:
    """Execute a background scan (stub).

    Phase 1 behavior: marks the scan RUNNING, performs no collection,
    and returns the context unchanged otherwise. The Phase 2 pipeline
    replaces the `pass` below with collector → analyzer execution.
    """
    logger.info("Scan %s starting (stub)", context.scan_id)
    context.state = ScanStatus.RUNNING
    # Phase 2: collect → analyze → score → persist → COMPLETED
    return context
