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
        database_url = "postgresql+asyncpg://" + database_url[len("postgres://"):]
    elif database_url.startswith("postgresql://"):
        database_url = "postgresql+asyncpg://" + database_url[len("postgresql://"):]

    # asyncpg does not support sslmode; replace with ssl=true
    database_url = database_url.replace("sslmode=require", "ssl=true")
    database_url = database_url.replace("sslmode=prefer", "ssl=true")
    database_url = database_url.replace("sslmode=verify-full", "ssl=true")
    database_url = database_url.replace("sslmode=disable", "")

    return database_url
