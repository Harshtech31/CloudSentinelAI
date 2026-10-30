"""
AWS S3 Collector for CloudSentinel AI.

Enumerates S3 buckets and discovers security postures: ACLs, Public Access
Blocks, default encryption, versioning, and server access logging.
"""

from typing import Any

from botocore.exceptions import BotoCoreError, ClientError

from app.collectors.aws import get_aws_client
from app.collectors.base import BaseCollector
from app.core.logging import logger


class S3Collector(BaseCollector):
    """Collects S3 buckets and their security posture from AWS."""

    provider = "aws"

    def collect(self) -> dict[str, list[dict[str, Any]]]:
        """Collect S3 buckets and probe their configuration settings."""
        try:
            s3 = get_aws_client("s3")
        except Exception as exc:
            logger.warning("Failed to initialize AWS S3 client: %s", exc)
            self.record("s3_buckets", [])
            return self.resources

        buckets: list[dict[str, Any]] = []
        try:
            res = s3.list_buckets()
            raw_buckets = res.get("Buckets", [])
        except Exception as exc:
            logger.warning("Error listing S3 buckets: %s", exc)
            self.record("s3_buckets", [])
            return self.resources

        for b in raw_buckets:
            name = b["Name"]
            arn = f"arn:aws:s3:::{name}"
            region = "us-east-1"
            try:
                loc_res = s3.get_bucket_location(Bucket=name)
                region = loc_res.get("LocationConstraint") or "us-east-1"
                if region == "EU":
                    region = "eu-west-1"
            except Exception:
                pass

            # Per-bucket security metadata
            bucket_data: dict[str, Any] = {
                "id": name,
                "name": name,
                "arn": arn,
                "region": region,
                "created_at": b.get("CreationDate", "").isoformat()
                if hasattr(b.get("CreationDate", ""), "isoformat")
                else str(b.get("CreationDate", "")),
                "is_public": False,
                "public_access_block": {},
                "acl_grants": [],
                "encrypted": False,
                "encryption_type": None,
                "versioning_enabled": False,
                "logging_enabled": False,
            }

            # 1. Public Access Block
            try:
                pab_res = s3.get_public_access_block(Bucket=name)
                pab_cfg = pab_res.get("PublicAccessBlockConfiguration", {})
                bucket_data["public_access_block"] = pab_cfg
            except ClientError as exc:
                if exc.response["Error"]["Code"] == "NoSuchPublicAccessBlockConfiguration":
                    bucket_data["public_access_block"] = {
                        "BlockPublicAcls": False,
                        "IgnorePublicAcls": False,
                        "BlockPublicPolicy": False,
                        "RestrictPublicBuckets": False,
                    }

            # 2. Policy Status (IsPublic)
            try:
                ps_res = s3.get_bucket_policy_status(Bucket=name)
                if ps_res.get("PolicyStatus", {}).get("IsPublic"):
                    bucket_data["is_public"] = True
            except ClientError:
                pass

            # 3. ACL Grants (AllUsers / AuthenticatedUsers)
            try:
                acl_res = s3.get_bucket_acl(Bucket=name)
                for grant in acl_res.get("Grants", []):
                    grantee = grant.get("Grantee", {})
                    uri = grantee.get("URI", "")
                    perm = grant.get("Permission", "")
                    if "AllUsers" in uri or "AuthenticatedUsers" in uri:
                        bucket_data["is_public"] = True
                        bucket_data["acl_grants"].append({"grantee": uri, "permission": perm})
            except ClientError:
                pass

            # 4. Default Encryption
            try:
                enc_res = s3.get_bucket_encryption(Bucket=name)
                rules = (
                    enc_res.get("ServerSideEncryptionConfiguration", {}).get("Rules", [])
                )
                if rules:
                    bucket_data["encrypted"] = True
                    bucket_data["encryption_type"] = (
                        rules[0]
                        .get("ApplyServerSideEncryptionByDefault", {})
                        .get("SSEAlgorithm")
                    )
            except ClientError as exc:
                if exc.response["Error"]["Code"] != "ServerSideEncryptionConfigurationNotFoundError":
                    logger.debug("S3 encryption read error for %s: %s", name, exc)

            # 5. Versioning
            try:
                ver_res = s3.get_bucket_versioning(Bucket=name)
                bucket_data["versioning_enabled"] = ver_res.get("Status") == "Enabled"
            except ClientError:
                pass

            # 6. Logging
            try:
                log_res = s3.get_bucket_logging(Bucket=name)
                bucket_data["logging_enabled"] = "LoggingEnabled" in log_res
            except ClientError:
                pass

            buckets.append(bucket_data)

        self.record("s3_buckets", buckets)
        return self.resources


__all__ = ["S3Collector"]
