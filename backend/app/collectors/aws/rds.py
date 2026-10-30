"""
AWS RDS Collector for CloudSentinel AI.

Enumerates RDS databases, storage encryption status, public accessibility,
and security group bindings across configured AWS regions.
"""

from typing import Any

from app.collectors.aws import get_aws_client
from app.collectors.base import BaseCollector
from app.core.config import settings
from app.core.logging import logger


class RDSCollector(BaseCollector):
    """Collects RDS instances and their security posture from AWS."""

    provider = "aws"

    def __init__(self, regions: list[str] | None = None) -> None:
        super().__init__(regions=regions or [settings.AWS_DEFAULT_REGION])

    def collect(self) -> dict[str, list[dict[str, Any]]]:
        """Collect RDS database instances across configured regions."""
        rds_instances: list[dict[str, Any]] = []

        for region in self.regions:
            try:
                rds = get_aws_client("rds", region=region)
                paginator = rds.get_paginator("describe_db_instances")
                for page in paginator.paginate():
                    for db in page.get("DBInstances", []):
                        db_id = db["DBInstanceIdentifier"]
                        arn = db.get(
                            "DBInstanceArn",
                            f"arn:aws:rds:{region}:::db:{db_id}",
                        )
                        sgs = [
                            sg.get("VpcSecurityGroupId")
                            for sg in db.get("VpcSecurityGroups", [])
                            if sg.get("Status") == "active"
                        ]

                        rds_instances.append(
                            {
                                "id": db_id,
                                "name": db_id,
                                "arn": arn,
                                "region": region,
                                "engine": db.get("Engine"),
                                "engine_version": db.get("EngineVersion"),
                                "storage_encrypted": db.get("StorageEncrypted", False),
                                "kms_key_id": db.get("KmsKeyId"),
                                "publicly_accessible": db.get("PubliclyAccessible", False),
                                "backup_retention_period": db.get("BackupRetentionPeriod", 0),
                                "multi_az": db.get("MultiAZ", False),
                                "auto_minor_version_upgrade": db.get(
                                    "AutoMinorVersionUpgrade", True
                                ),
                                "security_groups": sgs,
                            }
                        )
            except Exception as exc:
                logger.warning("Error collecting RDS instances in %s: %s", region, exc)

        self.record("rds_instances", rds_instances)
        return self.resources


__all__ = ["RDSCollector"]
