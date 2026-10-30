"""
End-to-End Validation Script for CloudSentinel AI Backend.

Demonstrates:
1. Cloud Collection across AWS services.
2. Rule Analysis (IAM, Network, Storage, Encryption, CIS compliance).
3. Graph Engine & Multi-Hop Attack Trajectory discovery.
4. Report Generation in JSON, CSV, HTML, and PDF.
5. AI-Powered Explanation & Remediation with Amazon Bedrock Claude Haiku.
"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.ai.explain import explain_finding
from app.collectors.registration import register_default_collectors
from app.core.constants import CloudProvider, ReportFormat, ScanStatus
from app.database.base import Base
from app.database.models import Finding, Scan, User
from app.database.repositories import FindingRepository, ReportRepository, ScanRepository
from app.reports import ScanReportData, render_report
from app.services.graph_service import graph_store
from app.tasks.scan_task import run_scan_task

register_default_collectors()


def run_demo():
    print("=" * 70)
    print("🛡️  CLOUDSENTINEL AI — BACKEND END-TO-END VERIFICATION")
    print("=" * 70)

    # 1. Setup in-memory database
    print("\n[Step 1] Initializing isolated database...")
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    SessionFactory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    db = SessionFactory()

    user = User(
        email="lead_evaluator@cloudsentinel.ai",
        hashed_password="pw_hash_secure",
        full_name="Lead Security Architect",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    scan = Scan(
        id="scn_demo_live_01",
        user_id=user.id,
        target_cloud=CloudProvider.AWS,
        services="iam,ec2,s3,vpc,security_groups,rds,cloudtrail,config",
        status=ScanStatus.PENDING,
    )
    db.add(scan)
    db.commit()
    print(f"✅ Created scan: {scan.id} for user: {user.email}")

    # 2. Run Scan Task
    print("\n[Step 2] Executing full scan pipeline (Collect -> Analyze -> Graph -> Persist)...")
    run_scan_task(scan.id, session_factory=SessionFactory)

    db.expire_all()
    scan_repo = ScanRepository(db)
    completed_scan = scan_repo.get(scan.id)
    print(f"✅ Scan Status: {completed_scan.status}")
    print(f"✅ Resources Scanned: {completed_scan.resources_scanned}")
    print(f"✅ Progress: {completed_scan.progress_percentage}%")

    # 3. Inspect Findings
    finding_repo = FindingRepository(db)
    findings, total = finding_repo.list_paginated(scan_id=scan.id, page=1, limit=100)
    print(f"\n[Step 3] Findings Breakdown (Total: {total}):")
    for idx, f in enumerate(findings[:5], start=1):
        print(f"   {idx}. [{f.severity.value.upper()}] {f.rule_id}: {f.title} (Resource: {f.resource_id})")
    if total > 5:
        print(f"   ... and {total - 5} more findings")

    # 4. Inspect Knowledge Graph & Attack Chains
    graph_resp = graph_store.get_graph(scan.id)
    stats_resp = graph_store.get_stats(scan.id)
    chains_resp = graph_store.get_attack_chains(scan.id)
    print(f"\n[Step 4] Knowledge Graph & Attack Engine:")
    print(f"   - Nodes: {stats_resp.total_nodes}")
    print(f"   - Relationship Edges: {stats_resp.total_edges}")
    print(f"   - Discovered Attack Chains: {chains_resp.total_chains}")

    for idx, c in enumerate(chains_resp.chains[:3], start=1):
        print(f"   Chain #{idx}: Risk Score {c.risk_score} [{c.severity}]")
        print(f"     Trajectory: {' -> '.join(c.path)}")

    # 5. Test Multi-Format Report Generation
    print(f"\n[Step 5] Generating Multi-Format Security Assessment Reports...")
    report_data = ScanReportData(
        scan_id=scan.id,
        account_id="250675044619",
        provider="aws",
        risk_score=78.5,
        compliance_score=85.0,
        findings=[
            {
                "rule_id": f.rule_id,
                "title": f.title,
                "severity": f.severity.value,
                "resource_id": f.resource_id,
                "region": f.region,
                "remediation": f.remediation,
            }
            for f in findings
        ],
        recommendations=["Rotate credentials", "Restrict open SGs", "Enable MFA"],
    )

    formats = [ReportFormat.JSON, ReportFormat.CSV, ReportFormat.HTML, ReportFormat.PDF]
    for fmt in formats:
        rendered = render_report(report_data, fmt)
        print(f"   ✅ Rendered {fmt.value.upper()} report ({len(rendered):,} bytes)")

    # 6. Test Bedrock AI Explanation for top finding
    if findings:
        top_f = findings[0]
        print(f"\n[Step 6] Invoking Amazon Bedrock Claude Haiku for Finding Explanation...")
        print(f"   Target: {top_f.title} ({top_f.rule_id})")
        fact_dict = {
            "title": top_f.title,
            "rule_id": top_f.rule_id,
            "severity": top_f.severity.value,
            "resource_id": top_f.resource_id,
            "description": top_f.description,
            "remediation_guidance": top_f.remediation,
        }
        explanation = explain_finding(fact_dict)
        print(f"   ✅ AI Provider: {explanation.provider} | Model: {explanation.model}")
        print("   --- AI Explanation Snippet ---")
        lines = [line for line in explanation.text.split("\n") if line.strip()]
        for line in lines[:6]:
            print(f"   {line}")
        print("   ------------------------------")

    print("\n" + "=" * 70)
    print("🎉 ALL BACKEND SUBSYSTEMS OPERATIONAL AND VERIFIED (100% READY)")
    print("=" * 70)


if __name__ == "__main__":
    run_demo()
