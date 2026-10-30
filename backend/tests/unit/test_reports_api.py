"""
Unit tests for Report Generators (JSON, CSV, HTML, PDF) and Report REST Endpoints.
"""

from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from app.auth.jwt import create_access_token
from app.core.constants import CloudProvider, ReportFormat, ScanStatus
from app.database.models import Scan, User
from app.main import app
from app.reports import ScanReportData, render_report


@pytest.fixture
def sample_report_data():
    return ScanReportData(
        scan_id="scn_test_rep_1",
        account_id="250675044619",
        provider="aws",
        generated_at=datetime.now(UTC).isoformat(),
        risk_score=85.0,
        compliance_score=90.0,
        summary={"total_findings": 2, "critical_findings": 1},
        findings=[
            {
                "rule_id": "AWS-IAM-001",
                "severity": "HIGH",
                "resource_type": "AWS::IAM::User",
                "resource_id": "alice",
                "title": "MFA Not Enabled",
                "risk_score": 7.5,
                "region": "global",
                "status": "open",
                "remediation": "Enable MFA",
            },
            {
                "rule_id": "AWS-NET-001",
                "severity": "CRITICAL",
                "resource_type": "AWS::EC2::SecurityGroup",
                "resource_id": "sg-open",
                "title": "Public SSH Allowed",
                "risk_score": 9.5,
                "region": "us-east-1",
                "status": "open",
                "remediation": "Restrict port 22",
            },
        ],
        recommendations=["Enable MFA", "Restrict SSH"],
    )


def test_render_report_all_formats(sample_report_data):
    # 1. JSON
    json_bytes = render_report(sample_report_data, ReportFormat.JSON)
    assert b"scn_test_rep_1" in json_bytes
    assert b"AWS-IAM-001" in json_bytes

    # 2. CSV
    csv_bytes = render_report(sample_report_data, ReportFormat.CSV)
    assert b"rule_id,severity,resource_type" in csv_bytes
    assert b"AWS-IAM-001,HIGH" in csv_bytes

    # 3. HTML
    html_bytes = render_report(sample_report_data, ReportFormat.HTML)
    assert b"<!DOCTYPE html>" in html_bytes
    assert b"CloudSentinel" in html_bytes
    assert b"AWS-NET-001" in html_bytes

    # 4. PDF
    pdf_bytes = render_report(sample_report_data, ReportFormat.PDF)
    assert pdf_bytes.startswith(b"%PDF-")


def test_reports_api_generate_and_download(sample_report_data):
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import StaticPool

    from app.database.base import Base
    from app.database.session import get_db

    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session = TestingSession()

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    try:
        # Create user and scan
        user = User(
            email="report_tester@example.com",
            hashed_password="pw",
            full_name="Tester",
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        scan = Scan(
            id="scn_api_rep_test",
            user_id=user.id,
            target_cloud=CloudProvider.AWS,
            status=ScanStatus.COMPLETED,
        )
        session.add(scan)
        session.commit()

        token = create_access_token(user.id, extra_claims={"role": user.role})
        headers = {"Authorization": f"Bearer {token}"}

        # 1. POST /api/v1/reports/generate (HTML)
        res = client.post(
            "/api/v1/reports/generate",
            json={"scan_id": scan.id, "format": "html", "include_ai_explanations": True},
            headers=headers,
        )
        assert res.status_code == 202
        data = res.json()
        assert data["format"] == "html"
        assert "download_url" in data
        report_id = data["id"]

        # 2. GET /api/v1/reports/{report_id}/download
        dl_res = client.get(f"/api/v1/reports/{report_id}/download", headers=headers)
        assert dl_res.status_code == 200
        assert b"<!DOCTYPE html>" in dl_res.content

        # 3. GET /api/v1/reports (List)
        list_res = client.get("/api/v1/reports", headers=headers)
        assert list_res.status_code == 200
        list_data = list_res.json()
        assert len(list_data["reports"]) >= 1

    finally:
        session.close()
        app.dependency_overrides.pop(get_db, None)
