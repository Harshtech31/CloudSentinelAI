"""
AWS CloudTrail Collector for CloudSentinel AI.

Enumerates CloudTrail trails, verifies logging activity, multi-region status,
log file validation, and associated S3 storage buckets.
"""

from typing import Any

from botocore.exceptions import BotoCoreError, ClientError

from app.collectors.aws import get_aws_client
from app.collectors.base import BaseCollector
from app.core.config import settings
from app.core.logging import logger


class CloudTrailCollector(BaseCollector):
    """Collects CloudTrail trails and logging status from AWS regions."""

    provider = "aws"

    def __init__(self, regions: list[str] | None = None) -> None:
        super().__init__(regions=regions or [settings.AWS_DEFAULT_REGION])

    def collect(self) -> dict[str, list[dict[str, Any]]]:
        """Collect CloudTrail trails across configured regions."""
        trails: list[dict[str, Any]] = []

        for region in self.regions:
            try:
                ct = get_aws_client("cloudtrail", region=region)
                res = ct.describe_trails(includeShadowTrails=False)
                for trail in res.get("trailList", []):
                    name = trail["Name"]
                    arn = trail.get("TrailARN", f"arn:aws:cloudtrail:{region}:::trail/{name}")
                    is_multi_region = trail.get("IsMultiRegionTrail", False)
                    log_validation = trail.get("LogFileValidationEnabled", False)
                    s3_bucket = trail.get("S3BucketName")
                    kms_key = trail.get("KmsKeyId")

                    is_logging = False
                    try:
                        status_res = ct.get_trail_status(Name=arn)
                        is_logging = status_res.get("IsLogging", False)
                    except (ClientError, BotoCoreError):
                        pass

                    trails.append(
                        {
                            "id": name,
                            "name": name,
                            "arn": arn,
                            "region": region,
                            "is_multi_region": is_multi_region,
                            "is_logging": is_logging,
                            "log_file_validation_enabled": log_validation,
                            "s3_bucket_name": s3_bucket,
                            "kms_key_id": kms_key,
                        }
                    )
            except Exception as exc:
                logger.warning("Error collecting CloudTrail trails in %s: %s", region, exc)

        self.record("cloudtrail_trails", trails)
        return self.resources


__all__ = ["CloudTrailCollector"]
