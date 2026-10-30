"""
Onboarding Schemas for CloudSentinel AI.

Defines payloads and response contracts for AWS connection testing,
AI provider configuration, and onboarding status.
"""

from typing import Any

from pydantic import BaseModel, Field


class ValidateAWSRequest(BaseModel):
    aws_access_key_id: str = Field(
        ..., min_length=16, max_length=128, description="AWS Access Key ID"
    )
    aws_secret_access_key: str = Field(
        ..., min_length=16, max_length=256, description="AWS Secret Access Key"
    )
    aws_session_token: str | None = Field(
        None, max_length=4096, description="Optional STS Session Token"
    )
    region: str = Field("us-east-1", max_length=50, description="Target AWS region")


class ValidateAWSResponse(BaseModel):
    is_valid: bool
    account_id: str | None = None
    arn: str | None = None
    user_id: str | None = None
    error_message: str | None = None


class ValidateAIRequest(BaseModel):
    provider: str = Field(..., description="bedrock, openai, anthropic")
    api_key: str | None = Field(None, max_length=256)
    model: str | None = Field(None, max_length=64)
    aws_region: str | None = Field("us-east-1", max_length=50)


class ValidateAIResponse(BaseModel):
    is_valid: bool
    provider: str
    model: str | None = None
    error_message: str | None = None


class SaveOnboardingRequest(BaseModel):
    # AWS Credentials
    aws_access_key_id: str | None = Field(None, max_length=128)
    aws_secret_access_key: str | None = Field(None, max_length=256)
    aws_session_token: str | None = Field(None, max_length=4096)
    aws_default_region: str = Field("us-east-1", max_length=50)

    # AI Provider Settings
    ai_provider: str = Field(
        "bedrock", description="AI provider: bedrock, openai, anthropic, default"
    )
    openai_api_key: str | None = Field(None, max_length=256)
    openai_model: str = Field("gpt-4o-mini", max_length=64)
    anthropic_api_key: str | None = Field(None, max_length=256)
    anthropic_model: str = Field("claude-3-5-sonnet-20241022", max_length=64)

    # Automation
    trigger_initial_scan: bool = Field(
        True, description="Whether to trigger initial cloud audit upon completion"
    )


class OnboardingStatusResponse(BaseModel):
    is_onboarded: bool
    aws_configured: bool
    aws_account_id: str | None = None
    aws_default_region: str = "us-east-1"
    ai_provider: str = "bedrock"
    openai_configured: bool = False
    anthropic_configured: bool = False
    bedrock_configured: bool = True
    recommended_iam_policy: dict[str, Any] | None = None


__all__ = [
    "ValidateAWSRequest",
    "ValidateAWSResponse",
    "ValidateAIRequest",
    "ValidateAIResponse",
    "SaveOnboardingRequest",
    "OnboardingStatusResponse",
]
