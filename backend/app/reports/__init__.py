"""
Reports Package for CloudSentinel AI.

Renders scan results into exportable artifacts (JSON, CSV, HTML, PDF)
behind one facade: `render_report(scan_data, fmt)`. Every renderer
shares the same `ScanReportData` input so a scan can be exported to any
format without re-collecting anything.
"""

from app.core.constants import ReportFormat
from app.core.logging import logger
from app.reports.base import BaseRenderer, ScanReportData
from app.reports.csv import CSVRenderer
from app.reports.html import HTMLRenderer
from app.reports.json import JSONRenderer
from app.reports.pdf import PDFRenderer

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
]
