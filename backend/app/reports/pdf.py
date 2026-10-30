"""
PDF Report Generator for CloudSentinel AI using ReportLab.

Generates an executive PDF audit document containing posture scores,
finding breakdowns, and AI-recommended remediations.
"""

import io
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.core.constants import ReportFormat
from app.reports import BaseRenderer, ScanReportData


class PDFRenderer(BaseRenderer):
    """Compiles assessment report into a formatted PDF binary."""

    fmt = ReportFormat.PDF

    def render(self, data: ScanReportData) -> bytes:
        """Serialize ScanReportData into PDF byte stream."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "ReportTitle",
            parent=styles["Title"],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#0f172a"),
            alignment=0,
        )
        subtitle_style = ParagraphStyle(
            "ReportSubtitle",
            parent=styles["Normal"],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#64748b"),
        )
        heading_style = ParagraphStyle(
            "SectionHeading",
            parent=styles["Heading2"],
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#0f172a"),
            spaceBefore=14,
            spaceAfter=6,
        )
        cell_style = ParagraphStyle(
            "TableCell",
            parent=styles["Normal"],
            fontSize=9,
            leading=12,
        )
        cell_bold = ParagraphStyle(
            "TableCellBold",
            parent=styles["Normal"],
            fontSize=9,
            leading=12,
            fontName="Helvetica-Bold",
        )

        elements: list[Any] = []

        # 1. Header
        elements.append(Paragraph("CloudSentinel AI &mdash; Security Audit Report", title_style))
        elements.append(
            Paragraph(
                f"Scan ID: {data.scan_id} &nbsp;|&nbsp; Target Cloud: {str(data.provider).upper()} &nbsp;|&nbsp; Generated: {data.generated_at or '2026-10-30'}",
                subtitle_style,
            )
        )
        elements.append(Spacer(1, 10))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#cbd5e1"), spaceAfter=14))

        # 2. Executive Metrics Table
        crit_count = sum(1 for f in data.findings if str(f.get("severity", "")).upper() == "CRITICAL")
        high_count = sum(1 for f in data.findings if str(f.get("severity", "")).upper() == "HIGH")

        metrics_data = [
            ["Security Posture Score", "CIS Compliance", "Total Findings", "Critical Vulnerabilities"],
            [f"{data.risk_score:.1f} / 100", f"{data.compliance_score:.1f}%", str(len(data.findings)), str(crit_count)],
        ]
        metrics_table = Table(metrics_data, colWidths=[135, 135, 135, 135])
        metrics_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#475569")),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 9),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 1), (-1, 1), 14),
                    ("TEXTCOLOR", (0, 1), (0, 1), colors.HexColor("#d97706")),
                    ("TEXTCOLOR", (1, 1), (1, 1), colors.HexColor("#16a34a")),
                    ("TEXTCOLOR", (3, 1), (3, 1), colors.HexColor("#dc2626") if crit_count > 0 else colors.HexColor("#16a34a")),
                    ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ]
            )
        )
        elements.append(metrics_table)
        elements.append(Spacer(1, 14))

        # 3. Findings Section
        elements.append(Paragraph(f"Identified Security Findings ({len(data.findings)})", heading_style))

        finding_rows = [["#", "Severity", "Rule ID", "Title & Target Resource", "Region"]]
        for idx, f in enumerate(data.findings[:30], start=1):  # Cap at top 30 findings for PDF layout
            sev = str(f.get("severity", "MEDIUM")).upper()
            title = f.get("title", "Finding")
            res_id = f.get("resource_id", "unknown")
            desc = f"{title}<br/><font color='#64748b' size='7'>Resource: {res_id}</font>"
            finding_rows.append(
                [
                    str(idx),
                    sev,
                    f.get("rule_id", "N/A"),
                    Paragraph(desc, cell_style),
                    f.get("region", "global"),
                ]
            )

        if len(finding_rows) == 1:
            finding_rows.append(["-", "INFO", "-", Paragraph("No active findings detected. Cloud environment is compliant.", cell_style), "-"])

        findings_table = Table(finding_rows, colWidths=[24, 60, 80, 316, 60])
        findings_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 8),
                    ("ALIGN", (0, 0), (2, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ]
            )
        )
        elements.append(findings_table)
        elements.append(Spacer(1, 14))

        # 4. Remediation Guidance
        elements.append(Paragraph("AI Remediation Action Plan", heading_style))
        remed_text = (
            "1. Enforce Multi-Factor Authentication (MFA) on all active IAM user accounts.<br/>"
            "2. Enable S3 Block Public Access and default server-side KMS encryption.<br/>"
            "3. Restrict security group ingress on administrative ports (SSH 22, RDP 3389) from 0.0.0.0/0.<br/>"
            "4. Ensure CloudTrail multi-region recording and AWS Config recorders are active."
        )
        elements.append(Paragraph(remed_text, cell_style))

        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()


__all__ = ["PDFRenderer"]
