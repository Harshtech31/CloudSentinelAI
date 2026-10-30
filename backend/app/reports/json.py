"""
JSON Report Renderer for CloudSentinel AI.

Serializes scan assessment data into structured, machine-readable JSON.
"""

import json
from typing import Any

from app.core.constants import ReportFormat
from app.reports import BaseRenderer, ScanReportData


class JSONRenderer(BaseRenderer):
    """Stable, machine-readable JSON export used by APIs and integrations."""

    fmt = ReportFormat.JSON

    def render(self, data: ScanReportData) -> bytes:
        payload: dict[str, Any] = {
            "scan_id": data.scan_id,
            "account_id": data.account_id,
            "provider": str(data.provider),
            "generated_at": data.generated_at,
            "risk_score": data.risk_score,
            "compliance_score": data.compliance_score,
            "summary": data.summary,
            "findings_count": len(data.findings),
            "findings": data.findings,
            "recommendations": data.recommendations,
        }
        return json.dumps(payload, indent=2, default=str).encode("utf-8")


__all__ = ["JSONRenderer"]
