"""
Reports Package for CloudSentinel AI.

Renders scan results into exportable artifacts (JSON, CSV, HTML, PDF)
behind one facade: `render_report(scan_data, fmt)`. Every renderer
shares the same `ScanReportData` input so a scan can be exported to any
format without re-collecting anything.

Phase 1 scaffold: contract + dispatch + the JSON/CSV renderers.
HTML/PDF arrive in Phase 3 (roadmap_part3_risk_ai_dashboard.md —
"Report Generation").
"""

import csv
import io
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from app.core.constants import ReportFormat
from app.core.logging import logger


# --- Shared report model ---------------------------------------------------
@dataclass
class ScanReportData:
    """Format-agnostic report payload assembled by the scan pipeline."""

    scan_id: str
    account_id: str = "unknown"
    provider: str = "aws"
    generated_at: str = ""
    risk_score: float = 0.0
    compliance_score: float = 0.0
    summary: dict[str, Any] = field(default_factory=dict)
    findings: list[dict[str, Any]] = field(default_factory=list)
    recommendations: list[dict[str, Any]] = field(default_factory=list)


class BaseRenderer(ABC):
    """Contract for one export format."""

    fmt: ReportFormat

    @abstractmethod
    def render(self, data: ScanReportData) -> bytes:
        """Serialize the report payload to bytes."""
        raise NotImplementedError


# --- JSON renderer (real) ---------------------------------------------------
class JSONRenderer(BaseRenderer):
    """Stable, machine-readable export used by the API and tests."""

    fmt = ReportFormat.JSON

    def render(self, data: ScanReportData) -> bytes:
        payload = {
            "scan_id": data.scan_id,
            "account_id": data.account_id,
            "provider": data.provider,
            "generated_at": data.generated_at,
            "risk_score": data.risk_score,
            "compliance_score": data.compliance_score,
            "summary": data.summary,
            "findings": data.findings,
            "recommendations": data.recommendations,
        }
        return json.dumps(payload, indent=2, default=str).encode("utf-8")


# --- CSV renderer (real) ----------------------------------------------------
class CSVRenderer(BaseRenderer):
    """Flat findings table — the format auditors actually open."""

    fmt = ReportFormat.CSV

    _COLUMNS = (
        "rule_id",
        "severity",
        "resource_type",
        "resource_id",
        "title",
        "risk_score",
        "status",
    )

    def render(self, data: ScanReportData) -> bytes:
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(self._COLUMNS)
        for finding in data.findings:
            writer.writerow([finding.get(col, "") for col in self._COLUMNS])
        return buffer.getvalue().encode("utf-8")


# --- HTML renderer (stub; Phase 3 implements the styled report) --------------
class HTMLRenderer(BaseRenderer):
    """HTML export stub: valid minimal document, no styling yet."""

    fmt = ReportFormat.HTML

    def render(self, data: ScanReportData) -> bytes:
        rows = "".join(
            f"<tr><td>{f.get('rule_id', '')}</td><td>{f.get('severity', '')}</td>"
            f"<td>{f.get('title', '')}</td></tr>"
            for f in data.findings
        )
        html = (
            "<!DOCTYPE html><html><head><meta charset='utf-8'>"
            f"<title>CloudSentinel Report {data.scan_id}</title></head><body>"
            f"<h1>Scan {data.scan_id}</h1>"
            f"<p>Account {data.account_id} &middot; risk {data.risk_score}/10</p>"
            f"<table><tr><th>Rule</th><th>Severity</th><th>Title</th></tr>{rows}</table>"
            "</body></html>"
        )
        return html.encode("utf-8")


# --- PDF renderer (stub; Phase 3 implements via reportlab/weasyprint) --------
class PDFRenderer(BaseRenderer):
    """PDF export stub: raises until Phase 3 wires a PDF library."""

    fmt = ReportFormat.PDF

    def render(self, data: ScanReportData) -> bytes:
        raise NotImplementedError("PDF export lands in Phase 3; use JSON, CSV, or HTML for now")


_RENDERERS: dict[ReportFormat, type[BaseRenderer]] = {
    ReportFormat.JSON: JSONRenderer,
    ReportFormat.CSV: CSVRenderer,
    ReportFormat.HTML: HTMLRenderer,
    ReportFormat.PDF: PDFRenderer,
}


def render_report(data: ScanReportData, fmt: ReportFormat) -> bytes:
    """Render the report payload in the requested format."""
    renderer_cls = _RENDERERS.get(fmt)
    if renderer_cls is None:
        raise ValueError(f"Unsupported report format: {fmt!r}")
    logger.info("Rendering %s report for scan %s", fmt, data.scan_id)
    return renderer_cls().render(data)


__all__ = [
    "ScanReportData",
    "BaseRenderer",
    "JSONRenderer",
    "CSVRenderer",
    "HTMLRenderer",
    "PDFRenderer",
    "render_report",
    "json",
    "csv",
]
