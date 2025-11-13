"""Application configuration and settings."""
from functools import lru_cache
from typing import Any

from pydantic import Field, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "Autonomous Finance"
    app_version: str = "0.1.0"
    environment: str = Field(default="development", pattern="^(development|staging|production)$")
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    reload: bool = False

    # Database
    postgres_server: str = Field(default="localhost")
    postgres_port: int = Field(default=5432)
    postgres_user: str = Field(default="postgres")
    postgres_password: str = Field(default="postgres")
    postgres_db: str = Field(default="autonomous_finance")
    database_url: PostgresDsn | None = None

    @field_validator("database_url", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str | None, info: Any) -> str:
        """Build database URL from components."""
        if isinstance(v, str):
            return v
        return str(
            PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=info.data.get("postgres_user"),
                password=info.data.get("postgres_password"),
                host=info.data.get("postgres_server"),
                port=info.data.get("postgres_port"),
                path=f"{info.data.get('postgres_db') or ''}",
            )
        )

    # Redis
    redis_host: str = Field(default="localhost")
    redis_port: int = Field(default=6379)
    redis_db: int = Field(default=0)
    redis_password: str | None = None
    redis_url: RedisDsn | None = None

    @field_validator("redis_url", mode="before")
    @classmethod
    def assemble_redis_connection(cls, v: str | None, info: Any) -> str:
        """Build Redis URL from components."""
        if isinstance(v, str):
            return v
        password = info.data.get("redis_password")
        auth = f":{password}@" if password else ""
        return f"redis://{auth}{info.data.get('redis_host')}:{info.data.get('redis_port')}/{info.data.get('redis_db')}"

    # RabbitMQ
    rabbitmq_host: str = Field(default="localhost")
    rabbitmq_port: int = Field(default=5672)
    rabbitmq_user: str = Field(default="guest")
    rabbitmq_password: str = Field(default="guest")
    rabbitmq_vhost: str = Field(default="/")

    # Security
    secret_key: str = Field(
        default="CHANGE_ME_IN_PRODUCTION_TO_RANDOM_SECRET_KEY_AT_LEAST_32_CHARS"
    )
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days

    # CORS
    backend_cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Anthropic Claude
    anthropic_api_key: str = Field(default="")
    anthropic_model: str = Field(default="claude-sonnet-4-5-20250929")
    anthropic_max_tokens: int = Field(default=4096)
    anthropic_temperature: float = Field(default=0.0)

    # Google Cloud Vision
    google_application_credentials: str | None = None
    google_project_id: str | None = None

    # S3 / Object Storage
    s3_bucket: str = Field(default="autonomous-finance-docs")
    s3_region: str = Field(default="us-east-1")
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None

    # ERP Integrations
    netsuite_account_id: str | None = None
    netsuite_consumer_key: str | None = None
    netsuite_consumer_secret: str | None = None
    netsuite_token_id: str | None = None
    netsuite_token_secret: str | None = None

    quickbooks_client_id: str | None = None
    quickbooks_client_secret: str | None = None
    quickbooks_redirect_uri: str | None = None
    quickbooks_environment: str = Field(default="sandbox", pattern="^(sandbox|production)$")

    # Monitoring
    enable_metrics: bool = True
    enable_tracing: bool = True
    log_level: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")

    # Feature Flags
    enable_payment_execution: bool = False  # MVP: scheduling only
    enable_tax_filing: bool = False  # Phase 3
    enable_adaptive_learning: bool = False  # Phase 3


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
