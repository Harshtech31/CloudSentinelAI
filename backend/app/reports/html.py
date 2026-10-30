"""
HTML Security Assessment Report Generator for CloudSentinel AI.

Produces a standalone executive security audit report complete with CSS styling,
risk meters, finding breakdown, and AI remediation guidance.
"""

from typing import Any

from app.core.constants import ReportFormat
from app.reports import BaseRenderer, ScanReportData


class HTMLRenderer(BaseRenderer):
    """Renders comprehensive, styled HTML assessment reports."""

    fmt = ReportFormat.HTML

    def render(self, data: ScanReportData) -> bytes:
        """Render the ScanReportData into a complete styled HTML document."""
        finding_rows = []
        for idx, f in enumerate(data.findings, start=1):
            sev = str(f.get("severity", "MEDIUM")).upper()
            sev_class = {
                "CRITICAL": "badge-critical",
                "HIGH": "badge-high",
                "MEDIUM": "badge-medium",
                "LOW": "badge-low",
                "INFO": "badge-info",
            }.get(sev, "badge-info")

            remediation = f.get("remediation", f.get("remediation_guidance", "Review resource against AWS security best practices."))
            finding_rows.append(
                f"""
                <tr class="finding-row">
                    <td class="col-num">{idx}</td>
                    <td><span class="badge {sev_class}">{sev}</span></td>
                    <td class="col-rule"><code>{f.get("rule_id", "N/A")}</code></td>
                    <td>
                        <strong>{f.get("title", "Untitled finding")}</strong>
                        <div class="finding-desc">{f.get("description", "")}</div>
                        <div class="finding-remed"><strong>Remediation:</strong> {remediation}</div>
                    </td>
                    <td><code>{f.get("resource_id", "N/A")}</code><br><small>{f.get("region", "global")}</small></td>
                </tr>
                """
            )

        findings_html = "".join(finding_rows) if finding_rows else "<tr><td colspan='5' class='text-center'>No active findings detected. Cloud posture is compliant!</td></tr>"

        remed_items = []
        for rec in data.recommendations:
            if isinstance(rec, str):
                remed_items.append(f"<li>{rec}</li>")
            elif isinstance(rec, dict):
                remed_items.append(f"<li><strong>{rec.get('title', 'Action')}:</strong> {rec.get('action', '')}</li>")
        remediations_html = "".join(remed_items) if remed_items else "<li>Maintain automated periodic CSPM scans and enforce least-privilege IAM roles.</li>"

        crit_count = sum(1 for f in data.findings if str(f.get("severity", "")).upper() == "CRITICAL")
        high_count = sum(1 for f in data.findings if str(f.get("severity", "")).upper() == "HIGH")
        med_count = sum(1 for f in data.findings if str(f.get("severity", "")).upper() == "MEDIUM")
        low_count = sum(1 for f in data.findings if str(f.get("severity", "")).upper() == "LOW")

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CloudSentinel AI — Security Assessment Report ({data.scan_id})</title>
    <style>
        :root {{
            --bg-primary: #0f172a;
            --bg-card: #1e293b;
            --text-primary: #f8fafc;
            --text-muted: #94a3b8;
            --border-color: #334155;
            --accent-blue: #38bdf8;
            --crit: #ef4444;
            --high: #f97316;
            --med: #eab308;
            --low: #10b981;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-primary);
            color: var(--text-primary);
            padding: 2.5rem 1.5rem;
            line-height: 1.5;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        header {{
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 1.5rem;
            margin-bottom: 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
        }}
        .brand {{ font-size: 1.75rem; font-weight: 800; color: var(--accent-blue); letter-spacing: -0.5px; }}
        .brand span {{ color: var(--text-primary); }}
        .meta-tag {{ font-size: 0.875rem; color: var(--text-muted); }}
        
        /* Summary Grid */
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1rem; margin-bottom: 2rem; }}
        .card {{ background-color: var(--bg-card); border: 1px solid var(--border-color); border-radius: 8px; padding: 1.25rem; }}
        .card-label {{ font-size: 0.8rem; text-transform: uppercase; color: var(--text-muted); font-weight: 600; margin-bottom: 0.5rem; }}
        .card-value {{ font-size: 2rem; font-weight: 700; }}
        .score-good {{ color: var(--low); }}
        .score-warn {{ color: var(--med); }}
        .score-crit {{ color: var(--crit); }}

        /* Severities Banner */
        .sev-bar {{ display: flex; gap: 0.5rem; margin-bottom: 2rem; }}
        .sev-chip {{ flex: 1; padding: 0.75rem; border-radius: 6px; text-align: center; font-weight: 600; font-size: 0.9rem; }}
        .chip-crit {{ background: rgba(239, 68, 68, 0.15); border: 1px solid var(--crit); color: var(--crit); }}
        .chip-high {{ background: rgba(249, 115, 22, 0.15); border: 1px solid var(--high); color: var(--high); }}
        .chip-med {{ background: rgba(234, 179, 8, 0.15); border: 1px solid var(--med); color: var(--med); }}
        .chip-low {{ background: rgba(16, 185, 129, 0.15); border: 1px solid var(--low); color: var(--low); }}

        /* Findings Table */
        h2 {{ font-size: 1.25rem; font-weight: 700; margin-bottom: 1rem; color: var(--text-primary); }}
        table {{ width: 100%; border-collapse: collapse; margin-bottom: 2.5rem; background: var(--bg-card); border-radius: 8px; overflow: hidden; }}
        th, td {{ padding: 0.875rem 1rem; text-align: left; border-bottom: 1px solid var(--border-color); }}
        th {{ background-color: #172033; font-size: 0.8rem; text-transform: uppercase; color: var(--text-muted); letter-spacing: 0.5px; }}
        .col-num {{ width: 40px; color: var(--text-muted); }}
        .col-rule {{ width: 140px; }}
        .finding-desc {{ font-size: 0.875rem; color: var(--text-muted); margin-top: 0.25rem; }}
        .finding-remed {{ font-size: 0.85rem; color: var(--accent-blue); margin-top: 0.4rem; }}
        code {{ background: #0f172a; padding: 0.15rem 0.4rem; border-radius: 4px; font-size: 0.85rem; color: #e2e8f0; }}

        .badge {{ padding: 0.25rem 0.6rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 700; display: inline-block; }}
        .badge-critical {{ background: var(--crit); color: #fff; }}
        .badge-high {{ background: var(--high); color: #fff; }}
        .badge-medium {{ background: var(--med); color: #000; }}
        .badge-low {{ background: var(--low); color: #fff; }}
        .badge-info {{ background: var(--accent-blue); color: #000; }}

        /* Recommendations */
        .remed-box {{ background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 8px; padding: 1.5rem; }}
        .remed-box ul {{ padding-left: 1.25rem; color: var(--text-muted); }}
        .remed-box li {{ margin-bottom: 0.5rem; }}

        footer {{ margin-top: 3rem; text-align: center; font-size: 0.8rem; color: var(--text-muted); border-top: 1px solid var(--border-color); padding-top: 1.5rem; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div>
                <div class="brand">CloudSentinel <span>AI</span></div>
                <div class="meta-tag">Automated CSPM & Graph-Based Attack Path Assessment</div>
            </div>
            <div style="text-align: right;">
                <div><strong>Scan ID:</strong> <code>{data.scan_id}</code></div>
                <div class="meta-tag">Generated: {data.generated_at or 'Just now'} | Cloud: {str(data.provider).upper()}</div>
            </div>
        </header>

        <section class="grid">
            <div class="card">
                <div class="card-label">Security Posture Score</div>
                <div class="card-value score-warn">{data.risk_score:.1f} <span style="font-size: 1rem; color: var(--text-muted);">/ 100</span></div>
            </div>
            <div class="card">
                <div class="card-label">CIS Compliance Score</div>
                <div class="card-value score-good">{data.compliance_score:.1f}%</div>
            </div>
            <div class="card">
                <div class="card-label">Total Findings</div>
                <div class="card-value">{len(data.findings)}</div>
            </div>
            <div class="card">
                <div class="card-label">Critical Severity</div>
                <div class="card-value score-crit">{crit_count}</div>
            </div>
        </section>

        <section class="sev-bar">
            <div class="sev-chip chip-crit">Critical: {crit_count}</div>
            <div class="sev-chip chip-high">High: {high_count}</div>
            <div class="sev-chip chip-med">Medium: {med_count}</div>
            <div class="sev-chip chip-low">Low: {low_count}</div>
        </section>

        <section>
            <h2>Identified Security Misconfigurations ({len(data.findings)})</h2>
            <table>
                <thead>
                    <tr>
                        <th class="col-num">#</th>
                        <th>Severity</th>
                        <th class="col-rule">Rule ID</th>
                        <th>Title & Remediation</th>
                        <th>Target Resource</th>
                    </tr>
                </thead>
                <tbody>
                    {findings_html}
                </tbody>
            </table>
        </section>

        <section class="remed-box">
            <h2>AI Remediation Guidance & Action Plan</h2>
            <ul>
                {remediations_html}
            </ul>
        </section>

        <footer>
            Report generated by CloudSentinel AI Engine &middot; Powered by Amazon Bedrock Claude Haiku &middot; Confidential Security Audit
        </footer>
    </div>
</body>
</html>
"""
        return html_content.encode("utf-8")


__all__ = ["HTMLRenderer"]
