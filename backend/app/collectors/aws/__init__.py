"""
AWS Collector Package.

Provides boto3-based collectors for IAM, EC2, S3, VPC, Security Groups,
RDS, CloudTrail, and AWS Config. Individual service modules arrive in
Phase 2; this package currently exposes the shared session helper.
"""

from typing import Any

import boto3
from botocore.config import Config as BotoConfig

from app.core.config import settings


def get_aws_session(
    access_key: str | None = None,
    secret_key: str | None = None,
    session_token: str | None = None,
    region: str | None = None,
) -> Any:
    """Build a boto3 session, falling back to env/.aws credentials.

    Args:
        access_key: Optional explicit access key (per-scan override).
        secret_key: Optional explicit secret key (per-scan override).
        session_token: Optional STS session token (per-scan override).
        region: Optional region override; defaults to settings.AWS_DEFAULT_REGION.

    Returns:
        A boto3 Session bound to the resolved credentials/region.
    """
    return boto3.session.Session(
        aws_access_key_id=access_key or settings.AWS_ACCESS_KEY_ID or None,
        aws_secret_access_key=secret_key or settings.AWS_SECRET_ACCESS_KEY or None,
        aws_session_token=session_token or settings.AWS_SESSION_TOKEN or None,
        region_name=region or settings.AWS_DEFAULT_REGION,
    )


def get_aws_client(
    service: str,
    region: str | None = None,
    access_key: str | None = None,
    secret_key: str | None = None,
    session_token: str | None = None,
) -> Any:
    """Create a boto3 client with CloudSentinel retry/timeouts baked in.

    Uses standard-mode adaptive retry (max 5 attempts) and generous
    read timeouts suitable for large-account enumeration calls.
    """
    session = get_aws_session(access_key, secret_key, session_token, region)
    return session.client(
        service,
        region_name=region or settings.AWS_DEFAULT_REGION,
        config=BotoConfig(
            retries={"max_attempts": 5, "mode": "adaptive"},
            read_timeout=60,
            connect_timeout=10,
        ),
    )
