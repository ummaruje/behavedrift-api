"""
BehaveDrift API — Application Settings
Loaded from environment variables via pydantic-settings.
All config is documented in .env.example.
"""

from functools import lru_cache
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ---- Application ----
    app_name: str = "BehaveDrift API"
    app_env: str = "development"
    app_port: int = 8000
    debug: bool = False
    log_level: str = "INFO"
    log_format: str = "json"  # json | pretty
    allowed_hosts: list[str] = ["*"]

    # ---- Database ----
    database_url: str = (
        "postgresql+asyncpg://behavedrift:behavedrift_dev@localhost:5432/behavedrift_dev"
    )
    database_pool_size: int = 10
    database_max_overflow: int = 20
    database_echo: bool = False

    # ---- Redis ----
    redis_url: str = "redis://localhost:6379/0"

    # ---- Auth — JWT ----
    jwt_secret_key: str = "dev-only-secret-change-this-in-production"
    jwt_algorithm: str = "HS256"  # Use RS256 in production
    access_token_expire_minutes: int = 60

    # ---- Auth — API Key ----
    api_key_header_name: str = "X-API-Key"
    api_key_min_length: int = 32

    # ---- Drift Engine ----
    baseline_window_days: int = 28
    baseline_recency_weight: float = 1.5
    baseline_min_observations: int = 14
    baseline_recalculation_interval_hours: int = 6

    drift_alert_threshold_t1: float = 0.40
    drift_alert_threshold_t2: float = 0.60
    drift_alert_threshold_t3: float = 0.75
    drift_alert_threshold_t4: float = 0.90

    # ---- Webhooks ----
    webhook_signing_secret: str = "dev-webhook-secret"
    webhook_timeout_seconds: int = 10
    webhook_retry_attempts: int = 3
    webhook_retry_backoff_seconds: int = 30

    # ---- Rate Limiting ----
    rate_limit_requests_per_minute: int = 300
    rate_limit_burst: int = 50

    # ---- FHIR ----
    fhir_enabled: bool = False
    fhir_server_url: str = ""
    fhir_auth_token: str = ""

    # ---- Data Retention ----
    observation_retention_days: int = 2555  # 7 years
    alert_retention_days: int = 2555
    gdpr_audit_log_retention_days: int = 3650  # 10 years

    @field_validator(
        "drift_alert_threshold_t1",
        "drift_alert_threshold_t2",
        "drift_alert_threshold_t3",
        "drift_alert_threshold_t4",
        mode="before",
    )
    @classmethod
    def validate_threshold(cls, v: float) -> float:
        if not 0.0 <= float(v) <= 1.0:
            raise ValueError("Drift threshold must be between 0.0 and 1.0")
        return float(v)

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def drift_thresholds(self) -> dict[str, float]:
        return {
            "T1": self.drift_alert_threshold_t1,
            "T2": self.drift_alert_threshold_t2,
            "T3": self.drift_alert_threshold_t3,
            "T4": self.drift_alert_threshold_t4,
        }


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance — loaded once at startup."""
    return Settings()
