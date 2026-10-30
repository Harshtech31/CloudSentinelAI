"""
Storage Security Rule Analyzer for CloudSentinel AI.

Evaluates S3 buckets against CIS AWS Benchmark and CSPM best practices:
- AWS-S3-001: Publicly Accessible S3 Bucket (CIS 2.1.5, Critical)
- AWS-S3-002: S3 Bucket Versioning Disabled (CIS 2.1.4, Medium)
- AWS-S3-003: S3 Server Access Logging Disabled (CIS 2.1.3, Low)
"""

from typing import Any

from app.analyzers import BaseAnalyzer, RawFinding
from app.core.constants import Severity


class StorageAnalyzer(BaseAnalyzer):
    """Evaluates S3 buckets against storage security rules."""

    service = "storage"

    def analyze(self, resources: dict[str, list[dict[str, Any]]]) -> list[RawFinding]:
        """Run all storage rules over collected resources."""
        findings: list[RawFinding] = []
        findings.extend(self._check_public_bucket(resources))
        findings.extend(self._check_versioning(resources))
        findings.extend(self._check_logging(resources))
        return findings

    def _check_public_bucket(self, resources: dict[str, list[dict[str, Any]]]) -> list[RawFinding]:
        """Rule AWS-S3-001: S3 bucket allows public access."""
        findings: list[RawFinding] = []
        buckets = resources.get("s3_buckets", [])

        for b in buckets:
            name = b.get("name") or b.get("id", "unknown")
            arn = b.get("arn") or f"arn:aws:s3:::{name}"
            region = b.get("region", "us-east-1")

            pab = b.get("public_access_block", {})
            pab_disabled = not (
                pab.get("BlockPublicAcls")
                and pab.get("IgnorePublicAcls")
                and pab.get("BlockPublicPolicy")
                and pab.get("RestrictPublicBuckets")
            )
            is_public = b.get("is_public", False) or pab_disabled or bool(b.get("acl_grants"))

            if is_public:
                findings.append(
                    RawFinding(
                        rule_id="AWS-S3-001",
                        title=f"S3 Bucket Publicly Accessible: {name}",
                        description=(
                            f"S3 bucket '{name}' has public access enabled or lacks a complete "
                            "Public Access Block configuration, allowing unauthorized internet access to objects."
                        ),
                        severity=Severity.CRITICAL,
                        resource_type="AWS::S3::Bucket",
                        resource_id=name,
                        resource_arn=arn,
                        region=region,
                        remediation=(
                            f"Enable S3 Block Public Access on '{name}' via 'aws s3api "
                            f"put-public-access-block --bucket {name} --public-access-block-configuration "
                            "\"BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true\"'."
                        ),
                        remediation_url="https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html",
                        metadata={"bucket_name": name, "cis_control": "2.1.5"},
                    )
                )

        return findings

    def _check_versioning(self, resources: dict[str, list[dict[str, Any]]]) -> list[RawFinding]:
        """Rule AWS-S3-002: S3 bucket without object versioning."""
        findings: list[RawFinding] = []
        buckets = resources.get("s3_buckets", [])

        for b in buckets:
            if not b.get("versioning_enabled", False):
                name = b.get("name") or b.get("id", "unknown")
                arn = b.get("arn") or f"arn:aws:s3:::{name}"
                region = b.get("region", "us-east-1")
                findings.append(
                    RawFinding(
                        rule_id="AWS-S3-002",
                        title=f"S3 Bucket Versioning Disabled: {name}",
                        description=(
                            f"S3 bucket '{name}' does not have versioning enabled. Object versioning "
                            "protects against accidental deletion and ransomware overwrite attacks."
                        ),
                        severity=Severity.MEDIUM,
                        resource_type="AWS::S3::Bucket",
                        resource_id=name,
                        resource_arn=arn,
                        region=region,
                        remediation=(
                            f"Enable versioning on '{name}' via 'aws s3api put-bucket-versioning "
                            f"--bucket {name} --versioning-configuration Status=Enabled'."
                        ),
                        remediation_url="https://docs.aws.amazon.com/AmazonS3/latest/userguide/Versioning.html",
                        metadata={"bucket_name": name, "cis_control": "2.1.4"},
                    )
                )

        return findings

    def _check_logging(self, resources: dict[str, list[dict[str, Any]]]) -> list[RawFinding]:
        """Rule AWS-S3-003: S3 bucket server access logging disabled."""
        findings: list[RawFinding] = []
        buckets = resources.get("s3_buckets", [])

        for b in buckets:
            if not b.get("logging_enabled", False):
                name = b.get("name") or b.get("id", "unknown")
                arn = b.get("arn") or f"arn:aws:s3:::{name}"
                region = b.get("region", "us-east-1")
                findings.append(
                    RawFinding(
                        rule_id="AWS-S3-003",
                        title=f"S3 Server Access Logging Disabled: {name}",
                        description=(
                            f"S3 bucket '{name}' does not have server access logging enabled, "
                            "hindering auditability and security incident response."
                        ),
                        severity=Severity.LOW,
                        resource_type="AWS::S3::Bucket",
                        resource_id=name,
                        resource_arn=arn,
                        region=region,
                        remediation=(
                            f"Configure server access logging on bucket '{name}' targeting an audit log bucket."
                        ),
                        remediation_url="https://docs.aws.amazon.com/AmazonS3/latest/userguide/ServerLogs.html",
                        metadata={"bucket_name": name, "cis_control": "2.1.3"},
                    )
                )

        return findings


__all__ = ["StorageAnalyzer"]
