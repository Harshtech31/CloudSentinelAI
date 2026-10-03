"""
Background Scan Orchestrator for CloudSentinel AI.

Executes one scan end-to-end in five stages (roadmap_part2_core_pipeline.md
tasks 4-5, Member 1 track):

    PENDING → RUNNING → collect → analyze → graph → persist → COMPLETED

The task runs in FastAPI BackgroundTasks *after* the API response, so it
opens its own database session (injected as `session_factory` — tests pass
an in-memory SQLite factory). Collectors and the analyzer orchestrator are
likewise injectable: Member 2's collector stubs legitimately produce empty
resource sets today, and real boto3 collectors drop in without touching
this pipeline.

Progress is written to the scan row between stages so the frontend's
`GET /scan/{id}/status` polling shows real movement. Cancellation is
cooperative: between stages the task expires its session cache and
re-reads the scan row, so a CANCELLED written by the API session is
honored. Failures mark the scan FAILED with a readable message
(roadmap task 24) rather than raising.
"""

from collections.abc import Callable
from typing import Any

from botocore.exceptions import BotoCoreError, ClientError
from sqlalchemy.orm import Session

from app.analyzers import RawFinding
from app.analyzers.misconfigurations import MisconfigurationOrchestrator
from app.collectors.base import BaseCollector, CollectorError, CredentialsError
from app.core.constants import ScanStatus
from app.core.logging import logger
from app.database.models import Scan
from app.database.repositories import FindingRepository, ScanRepository
from app.graph import GraphBuilder
from app.graph.models import NodeType

# Collector registry — service name (as listed in ScanStartRequest.services)
# → collector class. Member 2's Phase 2 replaces the modules behind these
# keys with real boto3 collectors; the registry is the only touchpoint.
_COLLECTOR_REGISTRY: dict[str, type[BaseCollector]] = {}


def register_collector(service: str, collector_cls: type[BaseCollector]) -> None:
    """Register a collector class under a service name (pipeline extensibility)."""
    _COLLECTOR_REGISTRY[service] = collector_cls


def registered_services() -> list[str]:
    """Service names the pipeline can currently collect."""
    return sorted(_COLLECTOR_REGISTRY)


# Graph node types by collector resource-key prefix — typing is generic so
# the graph stage works for any provider's resource dictionaries.
_RESOURCE_NODE_TYPES: dict[str, NodeType] = {
    "iam": NodeType.IAM_USER,
    "ec2": NodeType.EC2_INSTANCE,
    "s3": NodeType.S3_BUCKET,
    "vpc": NodeType.VPC,
    "security_group": NodeType.SECURITY_GROUP,
    "rds": NodeType.RDS_INSTANCE,
}


def _node_type_for(resource_key: str) -> NodeType:
    """Best-effort NodeType for a collector resource key (fallback: VPC)."""
    for prefix, node_type in _RESOURCE_NODE_TYPES.items():
        if resource_key.startswith(prefix):
            return node_type
    return NodeType.VPC


def _build_collector(
    service: str,
    collector_factory: Callable[[str], BaseCollector] | None,
) -> BaseCollector | None:
    """Resolve the collector for one service.

    An injected factory wins (tests, custom pipelines); the module
    registry is the production default. None means "nothing collects
    this service" — logged and skipped, not fatal.
    """
    if collector_factory is not None:
        return collector_factory(service)
    registry_cls = _COLLECTOR_REGISTRY.get(service)
    return registry_cls() if registry_cls is not None else None


def _collect_stage(
    services: list[str],
    collector_factory: Callable[[str], BaseCollector] | None,
) -> dict[str, list[dict[str, Any]]]:
    """Run the resolved collector for each requested service.

    A missing collector for a requested service is logged and skipped —
    with Member 2's stub collectors a scan legitimately completes with
    zero resources rather than failing.
    """
    resources: dict[str, list[dict[str, Any]]] = {}
    for service in services:
        collector = _build_collector(service, collector_factory)
        if collector is None:
            logger.info("No collector available for %s — skipping", service)
            continue
        collected = collector.collect()
        for key, items in collected.items():
            resources.setdefault(key, []).extend(items)
    return resources


def _analyze_stage(
    resources: dict[str, list[dict[str, Any]]],
    analyzer: MisconfigurationOrchestrator,
) -> list[RawFinding]:
    """Run the analyzer orchestrator over collected resources."""
    return analyzer.run(resources)


def _graph_stage(resources: dict[str, list[dict[str, Any]]]) -> int:
    """Ingest collected resources into the knowledge graph.

    Returns the node count. The knowledge graph gives the Lead's graph
    endpoint data the moment a scan completes; attack-path extraction
    from this graph arrives with the Lead's Phase 2 wire-up, and the
    scan summary reports zero attack paths until then (never fake data).
    """
    builder = GraphBuilder()
    for resource_key, items in resources.items():
        node_type = _node_type_for(resource_key)
        for item in items:
            resource_id = str(item.get("arn") or item.get("id") or "")
            if not resource_id:
                continue
            builder.add_node(
                resource_id,
                label=str(item.get("name") or resource_id),
                node_type=node_type,
                arn=item.get("arn"),
                region=item.get("region"),
                properties={
                    k: v for k, v in item.items() if isinstance(v, (str, int, float, bool))
                },
            )
    graph_dict = builder.to_dict()
    node_count = len(graph_dict["nodes"])
    logger.info("Knowledge graph built: %d node(s)", node_count)
    return node_count


def _fresh_scan(db: Session, scan_id: str) -> Scan | None:
    """Re-read the scan row, bypassing the session's identity map.

    The API and the background task use different sessions; expiring
    cached state is what makes cooperative cancellation and cross-session
    progress visible here.
    """
    db.expire_all()
    return db.get(Scan, scan_id)


def run_scan_task(
    scan_id: str,
    *,
    session_factory: Callable[[], Session] | None = None,
    collector_factory: Callable[[str], BaseCollector] | None = None,
    analyzer: MisconfigurationOrchestrator | None = None,
) -> None:
    """Execute one scan end-to-end, persisting findings to the database.

    Designed for FastAPI BackgroundTasks: returns nothing, records all
    outcomes on the scan row, never raises.
    """
    from app.database.session import SessionLocal

    factory = session_factory or SessionLocal
    analyzer = analyzer or MisconfigurationOrchestrator()

    db = factory()
    try:
        repos = ScanRepository(db)
        finding_repo = FindingRepository(db)
        scan = repos.get(scan_id)
        if scan is None:
            logger.error("Scan %s not found — task aborting", scan_id)
            return

        services = [s for s in (scan.services or "").split(",") if s]

        try:
            # Pre-flight cancel check: never resurrect a CANCELLED scan by
            # transitioning it to RUNNING.
            if _fresh_scan(db, scan_id).status == ScanStatus.CANCELLED:
                logger.info("Scan %s already cancelled — not starting", scan_id)
                return
            repos.mark_running(scan)
            repos.update_progress(scan, 10)

            # Stage 1: collect (cooperative cancel point)
            if _fresh_scan(db, scan_id).status == ScanStatus.CANCELLED:
                logger.info("Scan %s cancelled before collection", scan_id)
                return
            resources = _collect_stage(services, collector_factory)
            repos.update_progress(scan, 40)

            # Stage 2: analyze
            raw_findings = _analyze_stage(resources, analyzer)
            repos.update_progress(scan, 60)

            # Stage 3: knowledge graph
            node_count = _graph_stage(resources)
            repos.update_progress(scan, 75)

            # Stage 4: persist findings
            finding_repo.bulk_create_from_raw(scan_id, raw_findings)
            repos.update_progress(scan, 90)

            # Stage 5: finalize
            fresh = _fresh_scan(db, scan_id)
            if fresh.status == ScanStatus.CANCELLED:
                logger.info("Scan %s cancelled during execution", scan_id)
                return
            repos.mark_completed(fresh)
            logger.info(
                "Scan %s completed: %d resource(s), %d finding(s), %d graph node(s)",
                scan_id,
                sum(len(v) for v in resources.values()),
                len(raw_findings),
                node_count,
            )

        except (CredentialsError, ClientError, BotoCoreError) as exc:
            logger.warning("Scan %s failed on cloud credentials/API: %s", scan_id, exc)
            fresh = _fresh_scan(db, scan_id)
            if fresh is not None:
                repos.mark_failed(fresh, f"Cloud API error: {exc}")
        except CollectorError as exc:
            fresh = _fresh_scan(db, scan_id)
            if fresh is not None:
                repos.mark_failed(fresh, f"Collector error: {exc}")
        except Exception as exc:  # noqa: BLE001 - the task must never die silently
            logger.exception("Scan %s failed unexpectedly", scan_id)
            fresh = _fresh_scan(db, scan_id)
            if fresh is not None:
                repos.mark_failed(fresh, f"Internal error: {exc}")
    finally:
        db.close()


__all__ = ["run_scan_task", "register_collector", "registered_services"]
