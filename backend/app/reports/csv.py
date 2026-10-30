"""
CSV Report Renderer for CloudSentinel AI.

Exports findings as a flat CSV table for security auditors and spreadsheet analysis.
"""

import csv
import io

from app.core.constants import ReportFormat
from app.reports.base import BaseRenderer, ScanReportData


class CSVRenderer(BaseRenderer):
    """Flat findings table — format for spreadsheets and external audits."""

    fmt = ReportFormat.CSV

    _COLUMNS = (
        "rule_id",
        "severity",
        "resource_type",
        "resource_id",
        "title",
        "risk_score",
        "region",
        "status",
        "remediation",
    )

    def render(self, data: ScanReportData) -> bytes:
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(self._COLUMNS)
        for finding in data.findings:
            writer.writerow([finding.get(col, "") for col in self._COLUMNS])
        return buffer.getvalue().encode("utf-8")


__all__ = ["CSVRenderer"]
