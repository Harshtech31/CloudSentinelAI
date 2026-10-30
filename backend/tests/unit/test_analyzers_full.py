"""
Comprehensive Unit Tests for All Security Rule Analyzers.

Verifies:
- IAMAnalyzer: MFA, admin wildcard, credentials age, inline policies
- NetworkingAnalyzer: open SSH, open RDP, open all traffic, default VPC, public subnet
- StorageAnalyzer: public S3, versioning, access logging
- EncryptionAnalyzer: unencrypted RDS, unencrypted S3, public RDS, backup retention
- ComplianceAnalyzer: CloudTrail status, validation, Config, CIS scoring
"""

from app.analyzers.compliance import ComplianceAnalyzer
from app.analyzers.encryption import EncryptionAnalyzer
from app.analyzers.iam import IAMAnalyzer
from app.analyzers.networking import NetworkingAnalyzer
from app.analyzers.storage import StorageAnalyzer


def test_iam_analyzer_rules():
    analyzer = IAMAnalyzer()
    resources = {
        "iam_users": [
            {
                "id": "u1",
                "name": "alice",
                "arn": "arn:aws:iam:::user/alice",
                "mfa_active": False,
                "access_keys": [
                    {"id": "AKIA1", "status": "Active", "created_at": "2020-01-01T00:00:00Z"}
                ],
                "inline_policies": ["inline1"],
            },
            {
                "id": "u2",
                "name": "bob",
                "arn": "arn:aws:iam:::user/bob",
                "mfa_active": True,
                "access_keys": [
                    {"id": "AKIA2", "status": "Active", "created_at": "2026-10-01T00:00:00Z"}
                ],
                "inline_policies": [],
            },
        ],
        "iam_policies": [
            {
                "id": "p1",
                "name": "AdminWildcard",
                "arn": "arn:aws:iam:::policy/AdminWildcard",
                "document": {"Statement": [{"Effect": "Allow", "Action": "*", "Resource": "*"}]},
            }
        ],
    }

    findings = analyzer.analyze(resources)
    rule_ids = {f.rule_id for f in findings}
    assert "AWS-IAM-001" in rule_ids  # alice MFA missing
    assert "AWS-IAM-002" in rule_ids  # AdminWildcard
    assert "AWS-IAM-003" in rule_ids  # AKIA1 older than 90 days
    assert "AWS-IAM-004" in rule_ids  # alice inline policy


def test_networking_analyzer_rules():
    analyzer = NetworkingAnalyzer()
    resources = {
        "security_groups": [
            {
                "id": "sg-open",
                "name": "open-sg",
                "region": "us-east-1",
                "has_open_ssh": True,
                "has_open_rdp": True,
                "allows_all_traffic": True,
            },
            {
                "id": "sg-closed",
                "name": "secure-sg",
                "region": "us-east-1",
                "has_open_ssh": False,
                "has_open_rdp": False,
                "allows_all_traffic": False,
            },
        ],
        "vpcs": [
            {"id": "vpc-def", "is_default": True, "region": "us-east-1"},
            {"id": "vpc-cust", "is_default": False, "region": "us-east-1"},
        ],
        "subnets": [
            {"id": "sub-pub", "map_public_ip_on_launch": True, "region": "us-east-1"},
            {"id": "sub-priv", "map_public_ip_on_launch": False, "region": "us-east-1"},
        ],
    }

    findings = analyzer.analyze(resources)
    rule_ids = {f.rule_id for f in findings}
    assert "AWS-NET-001" in rule_ids  # open SSH
    assert "AWS-NET-002" in rule_ids  # open RDP
    assert "AWS-NET-003" in rule_ids  # all traffic open
    assert "AWS-NET-004" in rule_ids  # default VPC
    assert "AWS-NET-005" in rule_ids  # subnet auto-assign public IP


def test_storage_analyzer_rules():
    analyzer = StorageAnalyzer()
    resources = {
        "s3_buckets": [
            {
                "name": "insecure-bucket",
                "is_public": True,
                "public_access_block": {"BlockPublicAcls": False},
                "versioning_enabled": False,
                "logging_enabled": False,
            },
            {
                "name": "secure-bucket",
                "is_public": False,
                "public_access_block": {
                    "BlockPublicAcls": True,
                    "IgnorePublicAcls": True,
                    "BlockPublicPolicy": True,
                    "RestrictPublicBuckets": True,
                },
                "versioning_enabled": True,
                "logging_enabled": True,
            },
        ]
    }

    findings = analyzer.analyze(resources)
    rule_ids = {f.rule_id for f in findings}
    assert "AWS-S3-001" in rule_ids  # public bucket
    assert "AWS-S3-002" in rule_ids  # no versioning
    assert "AWS-S3-003" in rule_ids  # no logging


def test_encryption_analyzer_rules():
    analyzer = EncryptionAnalyzer()
    resources = {
        "rds_instances": [
            {
                "id": "unenc-db",
                "region": "us-east-1",
                "storage_encrypted": False,
                "publicly_accessible": True,
                "backup_retention_period": 1,
            },
            {
                "id": "enc-db",
                "region": "us-east-1",
                "storage_encrypted": True,
                "publicly_accessible": False,
                "backup_retention_period": 14,
            },
        ],
        "s3_buckets": [
            {"name": "unenc-b", "encrypted": False},
            {"name": "enc-b", "encrypted": True},
        ],
    }

    findings = analyzer.analyze(resources)
    rule_ids = {f.rule_id for f in findings}
    assert "AWS-ENC-001" in rule_ids  # unencrypted RDS
    assert "AWS-ENC-002" in rule_ids  # unencrypted S3
    assert "AWS-ENC-003" in rule_ids  # public RDS
    assert "AWS-ENC-004" in rule_ids  # backup retention < 7 days


def test_compliance_analyzer_scoring():
    analyzer = ComplianceAnalyzer()
    resources = {
        "cloudtrail_trails": [
            {
                "name": "trail1",
                "is_logging": False,
                "is_multi_region_trail": False,
                "log_file_validation_enabled": False,
            }
        ],
        "config_recorders": [{"name": "rec1", "recording": False}],
    }

    findings = analyzer.analyze(resources)
    rule_ids = {f.rule_id for f in findings}
    assert "AWS-CIS-3.1" in rule_ids
    assert "AWS-CIS-3.2" in rule_ids
    assert "AWS-CIS-3.5" in rule_ids

    # Compliance score on findings
    score = analyzer.compliance_score(findings)
    assert 0.0 <= score < 100.0
