"""
Application configuration management via Pydantic Settings.
"""

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Global application settings and environment variable bindings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # General
    APP_NAME: str = "CloudSentinel AI"
    APP_VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Server Host / Port
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Security & JWT Auth
    SECRET_KEY: str = "change-this-in-production-to-a-super-secret-key-32-chars-min"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS Configuration
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                import json

                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, (list, tuple)):
            return [str(i) for i in v]
        return []

    # Database Configuration
    POSTGRES_USER: str = "cloudsentinel"
    POSTGRES_PASSWORD: str = "cloudsentinel_secure_pass"
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "cloudsentinel_db"

    DATABASE_URL: str = "postgresql+asyncpg://cloudsentinel:cloudsentinel_secure_pass@localhost:5432/cloudsentinel_db"
    DATABASE_SYNC_URL: str = "postgresql+psycopg2://cloudsentinel:cloudsentinel_secure_pass@localhost:5432/cloudsentinel_db"

    # Neo4j Graph Database (Optional)
    NEO4J_URI: str = "bolt://neo4j:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "neo4j_password"

    # AWS Credentials
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_DEFAULT_REGION: str = "us-east-1"
    AWS_SESSION_TOKEN: str = ""

    # AI Provider
    LLM_PROVIDER: str = "openai"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.1"
    AWS_BEDROCK_REGION: str = "us-east-1"

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"


settings = Settings()
