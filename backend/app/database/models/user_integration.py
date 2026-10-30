"""
User Integration ORM Model for CloudSentinel AI.

Stores per-user cloud credentials (AWS Access Keys, target regions) and AI Provider
configurations (Amazon Bedrock, OpenAI, Anthropic) for personalized tenant audits.
"""

from uuid import uuid4

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin


def _new_integration_id() -> str:
    return f"intg_{uuid4().hex[:12]}"


class UserIntegration(TimestampMixin, Base):
    """Per-user AWS cloud credentials and AI LLM configurations."""

    __tablename__ = "user_integrations"

    id: Mapped[str] = mapped_column(String(20), primary_key=True, default=_new_integration_id)
    user_id: Mapped[str] = mapped_column(
        String(20),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    is_onboarded: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # AWS Cloud Connection
    aws_access_key_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    aws_secret_access_key: Mapped[str | None] = mapped_column(String(256), nullable=True)
    aws_session_token: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    aws_default_region: Mapped[str] = mapped_column(String(50), default="us-east-1", nullable=False)
    aws_account_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    aws_caller_arn: Mapped[str | None] = mapped_column(String(256), nullable=True)

    # AI Provider Configuration ("bedrock" | "openai" | "anthropic" | "default")
    ai_provider: Mapped[str] = mapped_column(String(32), default="bedrock", nullable=False)
    openai_api_key: Mapped[str | None] = mapped_column(String(256), nullable=True)
    openai_model: Mapped[str] = mapped_column(String(64), default="gpt-4o-mini", nullable=False)
    anthropic_api_key: Mapped[str | None] = mapped_column(String(256), nullable=True)
    anthropic_model: Mapped[str] = mapped_column(
        String(64), default="claude-3-5-sonnet-20241022", nullable=False
    )
    bedrock_model: Mapped[str] = mapped_column(
        String(128), default="us.anthropic.claude-haiku-4-5-20251001-v1:0", nullable=False
    )

    user = relationship("User", back_populates="integration")

    def __repr__(self) -> str:
        return f"<UserIntegration {self.id} for user={self.user_id} (aws_account={self.aws_account_id}, ai={self.ai_provider})>"


__all__ = ["UserIntegration"]
