"""
AWS Collector Package.

Provides boto3-based collectors for IAM, EC2, S3, VPC, Security Groups,
RDS, CloudTrail, and AWS Config. Individual service modules arrive in
Phase 2; this package currently exposes the shared session helper.

Credentials policy: collection may only use AWS profiles named
`cloudsentinel-*` (e.g. `cloudsentinel-eval`). The guard in
`_resolve_profile` rejects anything else by design.
"""

from contextvars import ContextVar
from typing import Any

import boto3
from botocore.config import Config as BotoConfig
from botocore.exceptions import ProfileNotFound

from app.core.config import settings
from app.core.logging import logger

_SCAN_CREDENTIALS: ContextVar[dict[str, Any] | None] = ContextVar("scan_credentials", default=None)


def set_scan_credentials(
    access_key: str | None = None,
    secret_key: str | None = None,
    session_token: str | None = None,
    region: str | None = None,
) -> None:
    """Set explicit credentials for the current scan context (thread/task-safe)."""
    if access_key and secret_key:
        _SCAN_CREDENTIALS.set(
            {
                "access_key": access_key,
                "secret_key": secret_key,
                "session_token": session_token,
                "region": region,
            }
        )
    else:
        _SCAN_CREDENTIALS.set(None)


def clear_scan_credentials() -> None:
    """Clear context-scoped scan credentials."""
    _SCAN_CREDENTIALS.set(None)


def _resolve_profile() -> str | None:
    """Resolve the AWS CLI profile for collection, with an allowlist."""
    profile = settings.AWS_PROFILE.strip() or None
    if profile is None:
        return None
    if not profile.startswith("cloudsentinel-"):
        raise ValueError(
            f"Refusing AWS profile {profile!r}: only 'cloudsentinel-*' "
            "profiles may be used for collection."
        )
    return profile


def get_aws_session(
    access_key: str | None = None,
    secret_key: str | None = None,
    session_token: str | None = None,
    region: str | None = None,
) -> Any:
    """Build a boto3 session from context credentials, cloudsentinel-* profile, or explicit keys."""
    # Check context credentials if explicit parameters are omitted
    if not (access_key or secret_key):
        ctx = _SCAN_CREDENTIALS.get()
        if ctx:
            access_key = ctx.get("access_key")
            secret_key = ctx.get("secret_key")
            session_token = ctx.get("session_token")
            region = region or ctx.get("region")

    using_explicit_keys = bool(access_key or secret_key)
    profile = None if using_explicit_keys else _resolve_profile()

    kwargs: dict[str, Any] = {
        "region_name": region or settings.AWS_DEFAULT_REGION,
    }
    if not using_explicit_keys and profile is not None:
        kwargs["profile_name"] = profile
    if using_explicit_keys:
        kwargs["aws_access_key_id"] = access_key or None
        kwargs["aws_secret_access_key"] = secret_key or None
        kwargs["aws_session_token"] = session_token or None

    try:
        return boto3.session.Session(**kwargs)
    except ProfileNotFound:
        # Containers and CI have no ~/.aws — keep the app bootable and
        # let collection fail loudly at scan time with NoCredentialsError.
        logger.warning(
            "AWS profile %r not found in ~/.aws — falling back to the "
            "default credential chain. Scans will fail until credentials "
            "are configured.",
            profile,
        )
        kwargs.pop("profile_name", None)
        return boto3.session.Session(**kwargs)


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
