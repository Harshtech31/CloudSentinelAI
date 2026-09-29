"""
Unit tests for Member 2 Phase 1 scaffolding: collectors, analyzers,
orchestrator, and the scan task stub — using realistic AWS-shaped data.

Covers:
- BaseCollector contract (recording, summaries, abstract enforcement, errors)
- AWS session/client helpers (credential fallback, region handling)
- Every AWS service collector stub (IAM/EC2/S3/VPC/SG/RDS/CloudTrail/Config)
- BaseAnalyzer contract and RawFinding shape
- Rule-skeleton wiring (returns findings only from implemented rules)
- MisconfigurationOrchestrator fan-out and failure isolation
- ScanContext defaults and run_scan_task lifecycle
"""

from typing import Any

import pytest

from app.analyzers import BaseAnalyzer, RawFinding
from app.analyzers.compliance import ComplianceAnalyzer
from app.analyzers.encryption import EncryptionAnalyzer
from app.analyzers.iam import IAMAnalyzer
from app.analyzers.misconfigurations import MisconfigurationOrchestrator
from app.analyzers.networking import NetworkingAnalyzer
from app.analyzers.storage import StorageAnalyzer
from app.collectors.aws import get_aws_session
from app.collectors.aws.cloudtrail import CloudTrailCollector
from app.collectors.aws.config import AWSConfigCollector
from app.collectors.aws.ec2 import EC2Collector
from app.collectors.aws.iam import IAMCollector
from app.collectors.aws.rds import RDSCollector
from app.collectors.aws.s3 import S3Collector
from app.collectors.aws.security_groups import SecurityGroupCollector
from app.collectors.aws.vpc import VPCCollector
from app.collectors.base import BaseCollector, CollectorError, CredentialsError
from app.core.constants import ScanStatus
from app.tasks import ScanContext, run_scan_task

# ---------------------------------------------------------------------------
# Realistic AWS-shaped sample data (what Phase 2 collectors will produce)
# ---------------------------------------------------------------------------


def sample_iam_resources() -> dict[str, list[dict[str, Any]]]:
    """IAM resources shaped like real boto3 responses (Phase 2 contract)."""
    return {
        "iam_users": [
            {
                "user_name": "alice",
                "arn": "arn:aws:iam::123456789012:user/alice",
                "mfa_active": False,
                "console_access": True,
                "password_last_used": "2026-09-01T10:00:00Z",
                "access_keys": [
                    {"access_key_id": "AKIA...Alice", "status": "Active", "last_used_days": 120},
                ],
            },
            {
                "user_name": "svc-deployer",
                "arn": "arn:aws:iam::123456789012:user/svc-deployer",
                "mfa_active": True,
                "console_access": False,
                "access_keys": [],
            },
        ],
        "iam_roles": [
            {
                "role_name": "admin-role",
                "arn": "arn:aws:iam::123456789012:role/admin-role",
                "assume_role_policy": {"Statement": [{"Effect": "Allow", "Principal": "*"}]},
            },
        ],
        "iam_policies": [
            {
                "policy_name": "AdministratorAccess",
                "arn": "arn:aws:iam::aws:policy/AdministratorAccess",
                "document": {"Statement": [{"Effect": "Allow", "Action": "*", "Resource": "*"}]},
                "attachment_count": 1,
            },
        ],
    }


def sample_network_resources() -> dict[str, list[dict[str, Any]]]:
    """Security groups shaped like real EC2 describe_security_groups output."""
    return {
        "security_groups": [
            {
                "group_id": "sg-0abc123",
                "group_name": "public-web-sg",
                "vpc_id": "vpc-001",
                "ip_permissions": [
                    {
                        "from_port": 22,
                        "to_port": 22,
                        "ip_protocol": "tcp",
                        "ip_ranges": [{"cidr_ip": "0.0.0.0/0"}],
                    },
                ],
            },
            {
                "group_id": "sg-0def456",
                "group_name": "database-sg",
                "vpc_id": "vpc-001",
                "ip_permissions": [
                    {
                        "from_port": 5432,
                        "to_port": 5432,
                        "ip_protocol": "tcp",
                        "ip_ranges": [{"cidr_ip": "10.0.1.0/24"}],
                    },
                ],
            },
        ],
    }


def sample_storage_resources() -> dict[str, list[dict[str, Any]]]:
    """S3 buckets shaped like real collection output."""
    return {
        "s3_buckets": [
            {
                "name": "public-logs-bucket",
                "arn": "arn:aws:s3:::public-logs-bucket",
                "region": "us-east-1",
                "public_access_block": {
                    "block_public_acls": False,
                    "ignore_public_acls": False,
                    "block_public_policy": False,
                    "restrict_public_buckets": False,
                },
                "versioning_enabled": False,
                "default_encryption": None,
            },
            {
                "name": "private-data-bucket",
                "arn": "arn:aws:s3:::private-data-bucket",
                "region": "us-east-1",
                "public_access_block": {
                    "block_public_acls": True,
                    "ignore_public_acls": True,
                    "block_public_policy": True,
                    "restrict_public_buckets": True,
                },
                "versioning_enabled": True,
                "default_encryption": {"sse_algorithm": "AES256"},
            },
        ],
        "rds_instances": [
            {
                "db_instance_identifier": "prod-db",
                "arn": "arn:aws:rds:us-east-1:123456789012:db:prod-db",
                "engine": "postgres",
                "storage_encrypted": False,
                "backup_retention_days": 0,
            },
        ],
    }


# ---------------------------------------------------------------------------
# BaseCollector contract
# ---------------------------------------------------------------------------


class TestBaseCollector:
    def test_record_and_summary_track_resource_counts(self):
        collector = IAMCollector()
        collector.record("iam_users", [{"user_name": "alice"}])
        collector.record("iam_roles", [{"role_name": "r1"}, {"role_name": "r2"}])
        assert collector.summary() == {"iam_users": 1, "iam_roles": 2}

    def test_collectors_declare_aws_provider(self):
        for cls in (
            IAMCollector,
            EC2Collector,
            S3Collector,
            VPCCollector,
            SecurityGroupCollector,
            RDSCollector,
            CloudTrailCollector,
            AWSConfigCollector,
        ):
            assert cls.provider == "aws", cls.__name__

    def test_abstract_contract_enforced(self):
        class IncompleteCollector(BaseCollector):
            provider = "aws"

        with pytest.raises(TypeError):
            IncompleteCollector()  # type: ignore[abstract]

    def test_error_hierarchy(self):
        assert issubclass(CredentialsError, CollectorError)
        assert isinstance(CredentialsError("bad creds"), CollectorError)

    def test_default_region(self):
        assert IAMCollector().regions == ["us-east-1"]
        assert EC2Collector(regions=["eu-west-1"]).regions == ["eu-west-1"]


# ---------------------------------------------------------------------------
# AWS session helper
# ---------------------------------------------------------------------------


class TestAWSHelpers:
    def test_session_falls_back_to_defaults(self):
        session = get_aws_session()
        assert session.region_name == "us-east-1"

    def test_session_explicit_region_override(self):
        session = get_aws_session(region="ap-south-1")
        assert session.region_name == "ap-south-1"


# ---------------------------------------------------------------------------
# Every AWS service collector stub (Phase 1 contract: empty but structured)
# ---------------------------------------------------------------------------


class TestServiceCollectorStubs:
    def test_iam_collector_returns_structured_empty_sets(self):
        collector = IAMCollector()
        assert collector.collect() == {"iam_users": [], "iam_roles": [], "iam_policies": []}
        assert collector.summary() == {"iam_users": 0, "iam_roles": 0, "iam_policies": 0}

    def test_ec2_collector_returns_structured_empty_sets(self):
        assert EC2Collector().collect() == {"ec2_instances": []}

    def test_s3_collector_returns_structured_empty_sets(self):
        assert S3Collector().collect() == {"s3_buckets": []}

    def test_vpc_collector_returns_structured_empty_sets(self):
        assert VPCCollector().collect() == {"vpcs": [], "subnets": [], "route_tables": []}

    def test_security_group_collector_returns_structured_empty_sets(self):
        assert SecurityGroupCollector().collect() == {"security_groups": []}

    def test_rds_collector_returns_structured_empty_sets(self):
        assert RDSCollector().collect() == {"rds_instances": []}

    def test_cloudtrail_collector_returns_structured_empty_sets(self):
        assert CloudTrailCollector().collect() == {"cloudtrail_trails": []}

    def test_config_collector_returns_structured_empty_sets(self):
        assert AWSConfigCollector().collect() == {"config_recorders": []}

    def test_collect_service_delegates_to_collect(self):
        collector = S3Collector()
        assert collector.collect_service("s3_buckets") == []
        assert collector.resources == {"s3_buckets": []}


# ---------------------------------------------------------------------------
# RawFinding + BaseAnalyzer contract
# ---------------------------------------------------------------------------


class TestAnalyzerContract:
    def test_rawfinding_defaults_are_safe(self):
        finding = RawFinding(
            rule_id="AWS-IAM-001",
            title="Root MFA disabled",
            description="The root account has no MFA device.",
            severity="critical",
            resource_type="iam",
            resource_id="root",
        )
        assert finding.metadata == {}
        assert finding.resource_arn is None
        assert finding.remediation_url is None

    def test_analyzer_context_is_applied_to_findings(self):
        analyzer = IAMAnalyzer()
        finding = analyzer.make_finding(
            rule_id="AWS-IAM-001",
            title="t",
            description="d",
            severity="high",
            resource_id="root",
        )
        assert finding.resource_type == "iam"

    def test_abstract_analyzer_enforced(self):
        class IncompleteAnalyzer(BaseAnalyzer):
            service = "broken"

        with pytest.raises(TypeError):
            IncompleteAnalyzer()  # type: ignore[abstract]


# ---------------------------------------------------------------------------
# Rule skeletons: Phase 1 contract is "wired but produce no findings"
# ---------------------------------------------------------------------------


class TestRuleSkeletons:
    def test_iam_analyzer_runs_all_rules_without_findings(self):
        findings = IAMAnalyzer().analyze(sample_iam_resources())
        assert findings == []

    def test_networking_analyzer_runs_all_rules_without_findings(self):
        findings = NetworkingAnalyzer().analyze(sample_network_resources())
        assert findings == []

    def test_storage_and_encryption_analyzers_run_without_findings(self):
        assert StorageAnalyzer().analyze(sample_storage_resources()) == []
        assert EncryptionAnalyzer().analyze(sample_storage_resources()) == []

    def test_compliance_stub_reports_full_score_on_no_findings(self):
        compliance = ComplianceAnalyzer()
        assert compliance.analyze({}) == []
        assert compliance.compliance_score([]) == 100.0


# ---------------------------------------------------------------------------
# Orchestrator: fan-out + failure isolation
# ---------------------------------------------------------------------------


class TestMisconfigurationOrchestrator:
    def test_default_orchestrator_registers_five_analyzers(self):
        orchestrator = MisconfigurationOrchestrator()
        assert len(orchestrator.analyzers) == 5
        types = {type(a) for a in orchestrator.analyzers}
        assert types == {
            IAMAnalyzer,
            NetworkingAnalyzer,
            StorageAnalyzer,
            EncryptionAnalyzer,
            ComplianceAnalyzer,
        }

    def test_run_merges_findings_from_all_analyzers(self):
        class FindingAnalyzer(BaseAnalyzer):
            service = "fake"

            def analyze(self, resources):
                return [
                    self.make_finding(
                        rule_id="FAKE-001",
                        title="t",
                        description="d",
                        severity="low",
                        resource_id="r",
                    )
                ]

        orchestrator = MisconfigurationOrchestrator(
            analyzers=[FindingAnalyzer(), FindingAnalyzer()]
        )
        findings = orchestrator.run({"anything": []})
        assert len(findings) == 2
        assert all(f.resource_type == "fake" for f in findings)

    def test_failing_analyzer_is_isolated_not_fatal(self):
        class ExplodingAnalyzer(BaseAnalyzer):
            service = "boom"

            def analyze(self, resources):
                raise RuntimeError("AWS throttled")

        orchestrator = MisconfigurationOrchestrator(analyzers=[ExplodingAnalyzer(), IAMAnalyzer()])
        assert orchestrator.run(sample_iam_resources()) == []

    def test_run_against_realistic_resources_yields_no_findings_in_phase_1(self):
        resources: dict[str, list[dict[str, Any]]] = {}
        resources.update(sample_iam_resources())
        resources.update(sample_network_resources())
        resources.update(sample_storage_resources())
        assert MisconfigurationOrchestrator().run(resources) == []


# ---------------------------------------------------------------------------
# Scan task stub lifecycle
# ---------------------------------------------------------------------------


class TestScanTaskStub:
    def test_scan_context_defaults(self):
        ctx = ScanContext(scan_id="scn_83f12a9c")
        assert ctx.target_cloud.value == "aws"
        assert ctx.regions == ["us-east-1"]
        assert len(ctx.services) == 7
        assert ctx.state == ScanStatus.PENDING
        assert ctx.collected == {} and ctx.findings == []

    def test_run_scan_task_transitions_pending_to_running(self):
        ctx = run_scan_task(ScanContext(scan_id="scn_test", regions=["eu-west-1"]))
        assert ctx.state == ScanStatus.RUNNING
        assert ctx.scan_id == "scn_test"
        assert ctx.collected == {} and ctx.findings == []  # Phase 1: no collection

    def test_context_carries_per_scan_credentials_field(self):
        ctx = ScanContext(scan_id="scn_x", credentials={"AWS_ACCESS_KEY_ID": "AKIA...TEST"})
        assert ctx.credentials["AWS_ACCESS_KEY_ID"] == "AKIA...TEST"
