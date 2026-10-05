"""
Audit Log Repository for CloudSentinel AI.

Append-only audit trail (roadmap task 29). `log_scan_event` is called by
the scan API and the orchestrator inside the *same transaction* as the
scan mutation, so an audit entry can never trail its action.
"""

from sqlalchemy.orm import Session

from app.core.logging import logger
from app.database.models import AuditLog, Scan


class AuditLogRepository:
    """Append-only operations for `AuditLog` rows."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def log(
        self,
        *,
        actor_id: str | None,
        action: str,
        entity_type: str,
        entity_id: str,
        detail: str | None = None,
        commit: bool = True,
    ) -> AuditLog:
        """Append one audit entry.

        `commit=False` lets callers (scan lifecycle transitions) bundle
        the entry with the action's own transaction.
        """
        entry = AuditLog(
            actor_id=actor_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            detail=detail,
        )
        self.db.add(entry)
        if commit:
            self.db.commit()
            self.db.refresh(entry)
        logger.info("Audit: %s %s/%s (actor=%s)", action, entity_type, entity_id, actor_id)
        return entry

    # -- scan lifecycle events (roadmap task 29) ----------------------------

    def log_scan_created(self, scan: Scan, actor_id: str | None) -> AuditLog:
        return self.log(
            actor_id=actor_id,
            action="scan.created",
            entity_type="scan",
            entity_id=scan.id,
            detail=f"target={scan.target_cloud.value} services={scan.services}",
            commit=False,
        )

    def log_scan_completed(self, scan: Scan) -> AuditLog:
        return self.log(
            actor_id=scan.user_id,
            action="scan.completed",
            entity_type="scan",
            entity_id=scan.id,
            detail=f"resources_scanned={scan.resources_scanned}",
            commit=False,
        )

    def log_scan_failed(self, scan: Scan) -> AuditLog:
        return self.log(
            actor_id=scan.user_id,
            action="scan.failed",
            entity_type="scan",
            entity_id=scan.id,
            detail=(scan.error_message or "")[:500],
            commit=False,
        )

    def log_scan_cancelled(self, scan: Scan) -> AuditLog:
        return self.log(
            actor_id=scan.user_id,
            action="scan.cancelled",
            entity_type="scan",
            entity_id=scan.id,
            detail="Cancelled by user",
            commit=False,
        )

    def list_for_entity(self, entity_type: str, entity_id: str) -> list[AuditLog]:
        """Audit trail for one entity, oldest first."""
        from sqlalchemy import select

        return list(
            self.db.scalars(
                select(AuditLog)
                .where(AuditLog.entity_type == entity_type, AuditLog.entity_id == entity_id)
                .order_by(AuditLog.created_at.asc(), AuditLog.id.asc())
            ).all()
        )


__all__ = ["AuditLogRepository"]
