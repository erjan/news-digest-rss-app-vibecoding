from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = ""
    gemini_api_key: str = ""
    google_api_key: str = ""
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    otel_enabled: bool = False
    otel_exporter_otlp_endpoint: str = "http://otel-collector:4317"
    otel_exporter_otlp_insecure: bool = True
    otel_service_name: str = "news-digest-api"


settings = Settings()


def to_async_database_url(database_url: str) -> str:
    """Normalize common Postgres URL formats to SQLAlchemy asyncpg format."""
    if database_url.startswith("postgres://"):
        return "postgresql+asyncpg://" + database_url[len("postgres://") :]
    if database_url.startswith("postgresql://"):
        return "postgresql+asyncpg://" + database_url[len("postgresql://") :]
    return database_url
