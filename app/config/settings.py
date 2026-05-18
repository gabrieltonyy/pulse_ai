"""
Configuration settings for Pulse AI application.
Uses Pydantic Settings for environment variable management.
"""
from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_INSECURE_SECRET_KEY = "your-secret-key-change-in-production"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application Settings
    app_name: str = "Pulse AI"
    app_version: str = "0.1.0"
    debug: bool = Field(default=False, validation_alias="DEBUG")
    demo_mode: bool = Field(default=False, validation_alias="DEMO_MODE")

    # Database Settings
    database_url: str = Field(
        default="postgresql+asyncpg://pulse_user:pulse_password@localhost:5432/pulse_ai",
        validation_alias="DATABASE_URL"
    )
    database_pool_size: int = Field(default=5, validation_alias="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=10, validation_alias="DATABASE_MAX_OVERFLOW")
    database_pool_timeout: int = Field(default=30, validation_alias="DATABASE_POOL_TIMEOUT")
    database_pool_recycle: int = Field(default=3600, validation_alias="DATABASE_POOL_RECYCLE")

    # Ticketmaster API Settings
    ticketmaster_api_key: str = Field(..., validation_alias="TICKETMASTER_API_KEY")
    ticketmaster_base_url: str = Field(
        default="https://app.ticketmaster.com/discovery/v2",
        validation_alias="TICKETMASTER_BASE_URL"
    )
    ticketmaster_default_size: int = Field(default=10, validation_alias="TICKETMASTER_DEFAULT_SIZE")
    ticketmaster_default_sort: str = Field(default="date,asc", validation_alias="TICKETMASTER_DEFAULT_SORT")
    ticketmaster_timeout: int = Field(default=8, validation_alias="TICKETMASTER_TIMEOUT")

    # Geoapify API Settings
    geoapify_api_key: str = Field(..., validation_alias="GEOAPIFY_API_KEY")
    geoapify_base_url: str = Field(
        default="https://api.geoapify.com/v2",
        validation_alias="GEOAPIFY_BASE_URL"
    )
    geoapify_default_radius: int = Field(default=1000, validation_alias="GEOAPIFY_DEFAULT_RADIUS")
    geoapify_default_limit: int = Field(default=5, validation_alias="GEOAPIFY_DEFAULT_LIMIT")
    geoapify_timeout: int = Field(default=6, validation_alias="GEOAPIFY_TIMEOUT")

    # OpenWeather API Settings
    openweather_api_key: str = Field(..., validation_alias="OPENWEATHER_API_KEY")
    openweather_base_url: str = Field(
        default="https://api.openweathermap.org/data/2.5",
        validation_alias="OPENWEATHER_BASE_URL"
    )
    openweather_units: str = Field(default="metric", validation_alias="OPENWEATHER_UNITS")
    openweather_lang: str = Field(default="en", validation_alias="OPENWEATHER_LANG")
    openweather_timeout: int = Field(default=6, validation_alias="OPENWEATHER_TIMEOUT")
    weather_forecast_horizon_days: int = Field(default=5, validation_alias="WEATHER_FORECAST_HORIZON_DAYS")

    # LLM Provider Settings
    llm_provider: str = Field(default="watsonx", validation_alias="LLM_PROVIDER")

    # watsonx.ai Settings
    watsonx_api_key: str = Field(..., validation_alias="WATSONX_API_KEY")
    watsonx_project_id: str = Field(..., validation_alias="WATSONX_PROJECT_ID")
    watsonx_url: str = Field(
        default="https://us-south.ml.cloud.ibm.com",
        validation_alias="WATSONX_URL"
    )
    watsonx_model: str = Field(
        default="ibm/granite-13b-chat-v2",
        validation_alias="WATSONX_MODEL"
    )
    watsonx_max_tokens: int = Field(default=2048, validation_alias="WATSONX_MAX_TOKENS")
    watsonx_temperature: float = Field(default=0.7, validation_alias="WATSONX_TEMPERATURE")
    watsonx_chat_model: Optional[str] = Field(default=None, validation_alias="WATSONX_CHAT_MODEL")
    intent_cache_ttl_seconds: int = Field(default=300, validation_alias="INTENT_CACHE_TTL_SECONDS")

    # Eventbrite Settings
    eventbrite_enabled: bool = Field(default=False, validation_alias="EVENTBRITE_ENABLED")
    eventbrite_api_key: Optional[str] = Field(default=None, validation_alias="EVENTBRITE_API_KEY")
    eventbrite_org_id: Optional[str] = Field(default=None, validation_alias="EVENTBRITE_ORG_ID")
    eventbrite_venue_id: Optional[str] = Field(default=None, validation_alias="EVENTBRITE_VENUE_ID")

    # API Cache Settings
    cache_ttl_events: int = Field(default=3600, validation_alias="CACHE_TTL_EVENTS")  # 1 hour
    cache_ttl_weather: int = Field(default=1800, validation_alias="CACHE_TTL_WEATHER")  # 30 minutes
    cache_ttl_venues: int = Field(default=86400, validation_alias="CACHE_TTL_VENUES")  # 24 hours
    context_enrichment_limit: int = Field(default=5, validation_alias="CONTEXT_ENRICHMENT_LIMIT")

    # CORS Settings
    cors_origins: list[str] = Field(
        default=["http://localhost:8000", "http://127.0.0.1:8000"],
        validation_alias="CORS_ORIGINS"
    )

    # Session Settings — SECRET_KEY is required; startup fails without a real value.
    secret_key: str = Field(..., validation_alias="SECRET_KEY")

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Reject placeholder secret keys that would make sessions trivially forgeable."""
        if v == _INSECURE_SECRET_KEY:
            raise ValueError(
                "SECRET_KEY must be set to a strong random value. "
                "The placeholder 'your-secret-key-change-in-production' is not allowed."
            )
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long.")
        return v

    @field_validator("llm_provider")
    @classmethod
    def validate_llm_provider(cls, v: str) -> str:
        """Validate LLM provider is supported."""
        allowed = ["watsonx", "openai", "anthropic"]
        if v.lower() not in allowed:
            raise ValueError(f"LLM provider must be one of {allowed}")
        return v.lower()

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Ensure PostgreSQL is being used."""
        if not v.startswith("postgresql"):
            raise ValueError("Database must be PostgreSQL (postgresql:// or postgresql+asyncpg://)")
        return v

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return not self.debug and not self.demo_mode

    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL for Alembic."""
        return self.database_url.replace("+asyncpg", "")


# Global settings instance
settings = Settings()

# Made with Bob
