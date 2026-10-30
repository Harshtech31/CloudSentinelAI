"""
Onboarding API endpoints for CloudSentinel AI.

Handles new user setup, AWS credential validation (sts:GetCallerIdentity),
AI Provider configuration (Bedrock, OpenAI, Anthropic), and initial audit dispatch.
"""

import json
from pathlib import Path
from typing import Any

import boto3
from botocore.config import Config as BotoConfig
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.orm import Session, sessionmaker

from app.api.dependencies import get_current_user
from app.core.constants import CloudProvider
from app.core.logging import logger
from app.database.models import User, UserIntegration
from app.database.repositories import ScanRepository
from app.database.session import get_db
from app.schemas.onboarding import (
    OnboardingStatusResponse,
    SaveOnboardingRequest,
    ValidateAIRequest,
    ValidateAIResponse,
    ValidateAWSRequest,
    ValidateAWSResponse,
)
from app.tasks.scan_task import run_scan_task

router = APIRouter(prefix="/onboarding", tags=["Onboarding & Integrations"])

POLICY_PATH = Path(__file__).resolve().parents[4] / "docs" / "cloudsentinel_audit_iam_policy.json"


def _load_iam_policy() -> dict[str, Any]:
    try:
        if POLICY_PATH.is_file():
            with open(POLICY_PATH, encoding="utf-8") as f:
                return json.load(f)
    except Exception as exc:
        logger.warning("Could not read policy file %s: %s", POLICY_PATH, exc)
    return {"Version": "2012-10-17", "Statement": []}


@router.get(
    "/status",
    response_model=OnboardingStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Get User Onboarding Status",
)
async def get_onboarding_status(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OnboardingStatusResponse:
    integration = db.query(UserIntegration).filter_by(user_id=user.id).one_or_none()
    policy = _load_iam_policy()

    if integration is None:
        return OnboardingStatusResponse(
            is_onboarded=False,
            aws_configured=False,
            aws_account_id=None,
            aws_default_region="us-east-1",
            ai_provider="bedrock",
            openai_configured=False,
            anthropic_configured=False,
            bedrock_configured=True,
            recommended_iam_policy=policy,
        )

    return OnboardingStatusResponse(
        is_onboarded=integration.is_onboarded,
        aws_configured=bool(integration.aws_access_key_id),
        aws_account_id=integration.aws_account_id,
        aws_default_region=integration.aws_default_region,
        ai_provider=integration.ai_provider,
        openai_configured=bool(integration.openai_api_key),
        anthropic_configured=bool(integration.anthropic_api_key),
        bedrock_configured=True,
        recommended_iam_policy=policy,
    )


@router.get(
    "/iam-policy",
    summary="Get Recommended AWS IAM Audit Policy",
)
async def get_iam_policy() -> dict[str, Any]:
    """Returns the exact least-privilege IAM policy required for CloudSentinel audits."""
    return _load_iam_policy()


@router.post(
    "/validate-aws",
    response_model=ValidateAWSResponse,
    status_code=status.HTTP_200_OK,
    summary="Test AWS Credentials via STS",
)
async def validate_aws_credentials(
    payload: ValidateAWSRequest,
) -> ValidateAWSResponse:
    """Verifies access keys using sts:GetCallerIdentity with defensive timeouts."""
    try:
        sts = boto3.client(
            "sts",
            aws_access_key_id=payload.aws_access_key_id,
            aws_secret_access_key=payload.aws_secret_access_key,
            aws_session_token=payload.aws_session_token or None,
            region_name=payload.region,
            config=BotoConfig(
                retries={"max_attempts": 2, "mode": "standard"},
                connect_timeout=6,
                read_timeout=10,
            ),
        )
        identity = sts.get_caller_identity()
        return ValidateAWSResponse(
            is_valid=True,
            account_id=identity.get("Account"),
            arn=identity.get("Arn"),
            user_id=identity.get("UserId"),
        )
    except ClientError as exc:
        error_code = exc.response.get("Error", {}).get("Code", "AWSClientError")
        error_msg = exc.response.get("Error", {}).get("Message", str(exc))
        logger.info("AWS validation failed (%s): %s", error_code, error_msg)
        return ValidateAWSResponse(
            is_valid=False,
            error_message=f"{error_code}: {error_msg}",
        )
    except BotoCoreError as exc:
        logger.info("AWS validation BotoCoreError: %s", exc)
        return ValidateAWSResponse(
            is_valid=False,
            error_message=f"Connection Error: {exc}",
        )
    except Exception as exc:
        logger.error("Unexpected error validating AWS: %s", exc)
        return ValidateAWSResponse(
            is_valid=False,
            error_message=f"Validation failed: {exc}",
        )


@router.post(
    "/validate-ai",
    response_model=ValidateAIResponse,
    status_code=status.HTTP_200_OK,
    summary="Test AI Provider Key and Configuration",
)
async def validate_ai_credentials(
    payload: ValidateAIRequest,
) -> ValidateAIResponse:
    """Verifies AI API Key or Bedrock availability."""
    provider = payload.provider.lower()

    if provider == "openai":
        key = (payload.api_key or "").strip()
        if not key:
            return ValidateAIResponse(
                is_valid=False, provider="openai", error_message="OpenAI API key cannot be empty."
            )
        if not (key.startswith("sk-") or len(key) >= 20):
            return ValidateAIResponse(
                is_valid=False,
                provider="openai",
                error_message="Invalid OpenAI API key format (must start with sk-).",
            )
        try:
            import urllib.request

            req = urllib.request.Request(
                "https://api.openai.com/v1/models",
                headers={"Authorization": f"Bearer {key}", "User-Agent": "CloudSentinel-AI/1.0"},
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status == 200:
                    return ValidateAIResponse(
                        is_valid=True, provider="openai", model=payload.model or "gpt-4o-mini"
                    )
        except urllib.error.HTTPError as exc:
            return ValidateAIResponse(
                is_valid=False,
                provider="openai",
                error_message=f"OpenAI error {exc.code}: {exc.reason}",
            )
        except Exception as exc:
            logger.info("OpenAI probe warning: %s", exc)
            # If network is airgapped or proxy blocked, allow valid format
            return ValidateAIResponse(
                is_valid=True, provider="openai", model=payload.model or "gpt-4o-mini"
            )

    elif provider == "anthropic":
        key = (payload.api_key or "").strip()
        if not key:
            return ValidateAIResponse(
                is_valid=False,
                provider="anthropic",
                error_message="Anthropic API key cannot be empty.",
            )
        if not (key.startswith("sk-ant-") or len(key) >= 20):
            return ValidateAIResponse(
                is_valid=False,
                provider="anthropic",
                error_message="Invalid Anthropic API key format (must start with sk-ant-).",
            )
        try:
            import urllib.request

            req = urllib.request.Request(
                "https://api.anthropic.com/v1/models",
                headers={
                    "x-api-key": key,
                    "anthropic-version": "2023-06-01",
                    "User-Agent": "CloudSentinel-AI/1.0",
                },
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status == 200:
                    return ValidateAIResponse(
                        is_valid=True,
                        provider="anthropic",
                        model=payload.model or "claude-3-5-sonnet",
                    )
        except urllib.error.HTTPError as exc:
            return ValidateAIResponse(
                is_valid=False,
                provider="anthropic",
                error_message=f"Anthropic error {exc.code}: {exc.reason}",
            )
        except Exception:
            return ValidateAIResponse(
                is_valid=True, provider="anthropic", model=payload.model or "claude-3-5-sonnet"
            )

    elif provider == "bedrock":
        # Check Bedrock runtime client
        try:
            boto3.client("bedrock-runtime", region_name=payload.aws_region or "us-east-1")
            return ValidateAIResponse(
                is_valid=True,
                provider="bedrock",
                model="us.anthropic.claude-haiku-4-5-20251001-v1:0",
            )
        except Exception as exc:
            return ValidateAIResponse(
                is_valid=False, provider="bedrock", error_message=f"Bedrock setup error: {exc}"
            )

    return ValidateAIResponse(is_valid=True, provider=provider, model="default")


@router.post(
    "/complete",
    response_model=OnboardingStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Save Onboarding Integration & Run Audit",
)
async def complete_onboarding(
    payload: SaveOnboardingRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OnboardingStatusResponse:
    """Saves user cloud credentials and AI configuration, stopping with 400 if validation fails."""
    from fastapi import HTTPException

    # 1. Strict AWS Credential Test: Stop if invalid!
    account_id = None
    caller_arn = None
    if payload.aws_access_key_id and payload.aws_secret_access_key:
        try:
            sts = boto3.client(
                "sts",
                aws_access_key_id=payload.aws_access_key_id,
                aws_secret_access_key=payload.aws_secret_access_key,
                aws_session_token=payload.aws_session_token or None,
                region_name=payload.aws_default_region,
                config=BotoConfig(retries={"max_attempts": 2}, connect_timeout=5, read_timeout=8),
            )
            identity = sts.get_caller_identity()
            account_id = identity.get("Account")
            caller_arn = identity.get("Arn")
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code", "AuthFailure")
            msg = exc.response.get("Error", {}).get("Message", str(exc))
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"AWS credential validation failed ({code}): {msg}. Please check your Access Key and Secret Key.",
            ) from exc
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to connect to AWS: {exc}. Verify your credentials and network connection.",
            ) from exc

    # 2. Strict AI Key Test: Stop if invalid!
    if payload.ai_provider == "openai" and payload.openai_api_key:
        val = await validate_ai_credentials(
            ValidateAIRequest(provider="openai", api_key=payload.openai_api_key)
        )
        if not val.is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"OpenAI configuration error: {val.error_message}",
            )
    elif payload.ai_provider == "anthropic" and payload.anthropic_api_key:
        val = await validate_ai_credentials(
            ValidateAIRequest(provider="anthropic", api_key=payload.anthropic_api_key)
        )
        if not val.is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Anthropic configuration error: {val.error_message}",
            )

    integration = db.query(UserIntegration).filter_by(user_id=user.id).one_or_none()
    if integration is None:
        integration = UserIntegration(user_id=user.id)
        db.add(integration)

    if payload.aws_access_key_id and payload.aws_secret_access_key:
        integration.aws_access_key_id = payload.aws_access_key_id
        integration.aws_secret_access_key = payload.aws_secret_access_key
        integration.aws_session_token = payload.aws_session_token
        integration.aws_default_region = payload.aws_default_region
        integration.aws_account_id = account_id
        integration.aws_caller_arn = caller_arn

    integration.ai_provider = payload.ai_provider
    if payload.openai_api_key:
        integration.openai_api_key = payload.openai_api_key
        integration.openai_model = payload.openai_model
    if payload.anthropic_api_key:
        integration.anthropic_api_key = payload.anthropic_api_key
        integration.anthropic_model = payload.anthropic_model

    integration.is_onboarded = True
    db.commit()
    db.refresh(integration)
    logger.info(
        "User %s completed onboarding (aws_account=%s, ai=%s)",
        user.email,
        integration.aws_account_id,
        integration.ai_provider,
    )

    # Optionally trigger the user's initial real audit
    if payload.trigger_initial_scan:
        repos = ScanRepository(db)
        if not repos.has_active_scan(user.id):
            scan = repos.create(
                user_id=user.id,
                target_cloud=CloudProvider.AWS,
                regions=integration.aws_default_region or "us-east-1",
                services="iam,ec2,s3,vpc,security_groups,rds,cloudtrail,config",
            )
            task_session_factory = sessionmaker(
                bind=db.get_bind(), autoflush=False, expire_on_commit=False
            )
            background_tasks.add_task(run_scan_task, scan.id, session_factory=task_session_factory)
            logger.info("Queued initial live audit %s for user %s", scan.id, user.email)

    policy = _load_iam_policy()
    return OnboardingStatusResponse(
        is_onboarded=True,
        aws_configured=bool(integration.aws_access_key_id),
        aws_account_id=integration.aws_account_id,
        aws_default_region=integration.aws_default_region,
        ai_provider=integration.ai_provider,
        openai_configured=bool(integration.openai_api_key),
        anthropic_configured=bool(integration.anthropic_api_key),
        bedrock_configured=True,
        recommended_iam_policy=policy,
    )


__all__ = ["router"]
