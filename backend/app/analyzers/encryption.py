"""
Encryption Security Rule Analyzer for CloudSentinel AI.

Evaluates data-at-rest encryption across cloud storage and database tiers:
- AWS-ENC-001: RDS Database Storage Unencrypted (CIS 2.3.1, High)
- AWS-ENC-002: S3 Bucket Default Encryption Disabled (CIS 2.1.1, High)
- AWS-ENC-003: RDS Database Publicly Accessible (CIS 2.3.2, Critical)
- AWS-ENC-004: RDS Automated Backup Retention Less than 7 Days (Medium)
"""

from typing import Any

from app.analyzers import BaseAnalyzer, RawFinding
from app.core.constants import Severity


class EncryptionAnalyzer(BaseAnalyzer):
    """Evaluates RDS and S3 data-at-rest encryption and database exposure."""

    service = "encryption"

    def analyze(self, resources: dict[str, list[dict[str, Any]]]) -> list[RawFinding]:
        """Run all encryption and data security checks over collected resources."""
        findings: list[RawFinding] = []
        findings.extend(self._check_unencrypted_rds(resources))
        findings.extend(self._check_unencrypted_s3(resources))
        findings.extend(self._check_public_rds(resources))
        findings.extend(self._check_rds_backup_retention(resources))
        return findings

    def _check_unencrypted_rds(
        self, resources: dict[str, list[dict[str, Any]]]
    ) -> list[RawFinding]:
        """Rule AWS-ENC-001: RDS storage encryption disabled at rest."""
        findings: list[RawFinding] = []
        rds_instances = resources.get("rds_instances", [])

        for db in rds_instances:
            if not db.get("storage_encrypted", False):
                db_id = db.get("id", "unknown")
                region = db.get("region", "global")
                arn = db.get("arn") or f"arn:aws:rds:{region}:::db:{db_id}"

                findings.append(
                    RawFinding(
                        rule_id="AWS-ENC-001",
                        title=f"RDS Instance Storage Unencrypted: {db_id}",
                        description=(
                            f"RDS database '{db_id}' in region {region} does not have storage "
                            "encryption enabled at rest using AWS KMS."
                        ),
                        severity=Severity.HIGH,
                        resource_type="AWS::RDS::DBInstance",
                        resource_id=db_id,
                        resource_arn=arn,
                        region=region,
                        remediation=(
                            f"Create an encrypted snapshot of '{db_id}' and restore to a new "
                            "encrypted RDS DB instance with AWS KMS encryption enabled."
                        ),
                        remediation_url="https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Overview.Encryption.html",
                        metadata={
                            "db_id": db_id,
                            "engine": db.get("engine"),
                            "cis_control": "2.3.1",
                        },
                    )
                )

        return findings

    def _check_unencrypted_s3(self, resources: dict[str, list[dict[str, Any]]]) -> list[RawFinding]:
        """Rule AWS-ENC-002: S3 bucket default server-side encryption disabled."""
        findings: list[RawFinding] = []
        buckets = resources.get("s3_buckets", [])

        for b in buckets:
            if not b.get("encrypted", False):
                name = b.get("name") or b.get("id", "unknown")
                region = b.get("region", "us-east-1")
                arn = b.get("arn") or f"arn:aws:s3:::{name}"

                findings.append(
                    RawFinding(
                        rule_id="AWS-ENC-002",
                        title=f"S3 Bucket Default Encryption Disabled: {name}",
                        description=(
                            f"S3 bucket '{name}' does not enforce server-side default encryption "
                            "(SSE-S3 or SSE-KMS), violating compliance standards."
                        ),
                        severity=Severity.HIGH,
                        resource_type="AWS::S3::Bucket",
                        resource_id=name,
                        resource_arn=arn,
                        region=region,
                        remediation=(
                            f"Enable default AES256 or KMS encryption on bucket '{name}' via "
                            f"'aws s3api put-bucket-encryption --bucket {name}'."
                        ),
                        remediation_url="https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucket-encryption.html",
                        metadata={"bucket_name": name, "cis_control": "2.1.1"},
                    )
                )

        return findings

    def _check_public_rds(self, resources: dict[str, list[dict[str, Any]]]) -> list[RawFinding]:
        """Rule AWS-ENC-003: RDS instance is publicly accessible."""
        findings: list[RawFinding] = []
        rds_instances = resources.get("rds_instances", [])

        for db in rds_instances:
            if db.get("publicly_accessible", False):
                db_id = db.get("id", "unknown")
                region = db.get("region", "global")
                arn = db.get("arn") or f"arn:aws:rds:{region}:::db:{db_id}"

                findings.append(
                    RawFinding(
                        rule_id="AWS-ENC-003",
                        title=f"RDS Instance Publicly Accessible: {db_id}",
                        description=(
                            f"RDS database instance '{db_id}' has the PubliclyAccessible flag set to True, "
                            "exposing the database engine endpoint directly to the internet."
                        ),
                        severity=Severity.CRITICAL,
                        resource_type="AWS::RDS::DBInstance",
                        resource_id=db_id,
                        resource_arn=arn,
                        region=region,
                        remediation=(
                            f"Modify RDS instance '{db_id}' to set PubliclyAccessible=False and "
                            "confine database connectivity to private VPC subnets."
                        ),
                        remediation_url="https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_VPC.WorkingWithRDSInstanceinaVPC.html",
                        metadata={"db_id": db_id, "cis_control": "2.3.2"},
                    )
                )

        return findings

    def _check_rds_backup_retention(
        self, resources: dict[str, list[dict[str, Any]]]
    ) -> list[RawFinding]:
        """Rule AWS-ENC-004: RDS automated backup retention period is less than 7 days."""
        findings: list[RawFinding] = []
        rds_instances = resources.get("rds_instances", [])

        for db in rds_instances:
            retention = db.get("backup_retention_period", 0)
            if retention < 7:
                db_id = db.get("id", "unknown")
                region = db.get("region", "global")
                arn = db.get("arn") or f"arn:aws:rds:{region}:::db:{db_id}"

                findings.append(
                    RawFinding(
                        rule_id="AWS-ENC-004",
                        title=f"RDS Backup Retention Less than 7 Days: {db_id}",
                        description=(
                            f"RDS database '{db_id}' has a backup retention period of {retention} day(s). "
                            "Best practice requires at least 7 days for disaster recovery."
                        ),
                        severity=Severity.MEDIUM,
                        resource_type="AWS::RDS::DBInstance",
                        resource_id=db_id,
                        resource_arn=arn,
                        region=region,
                        remediation=(
                            f"Update '{db_id}' backup retention period to >= 7 days via "
                            f"'aws rds modify-db-instance --db-instance-identifier {db_id} --backup-retention-period 7'."
                        ),
                        remediation_url="https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_WorkingWithAutomatedBackups.html",
                        metadata={"db_id": db_id, "retention_days": retention},
                    )
                )

        return findings


__all__ = ["EncryptionAnalyzer"]
