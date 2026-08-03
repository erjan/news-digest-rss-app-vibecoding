import re
from urllib.parse import urlencode, urlparse, parse_qs, urlunparse

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


def to_async_database_url(database_url: str) -> tuple[str, bool]:
    """Normalize Postgres URL to SQLAlchemy asyncpg format.

    Returns (url, ssl_required) — caller should pass ssl=True to connect_args
    when ssl_required is True.
    """
    if database_url.startswith("postgres://"):
        database_url = "postgresql+asyncpg://" + database_url[len("postgres://"):]
    elif database_url.startswith("postgresql://"):
        database_url = "postgresql+asyncpg://" + database_url[len("postgresql://"):]

    # Strip all ssl/sslmode query params — passed via connect_args instead
    parsed = urlparse(database_url)
    params = parse_qs(parsed.query, keep_blank_values=True)
    sslmode = params.pop("sslmode", ["disable"])[0]
    params.pop("ssl", None)
    ssl_required = sslmode in ("require", "verify-ca", "verify-full", "prefer", "allow")
    new_query = urlencode({k: v[0] for k, v in params.items()})
    clean_url = urlunparse(parsed._replace(query=new_query))
    return clean_url, ssl_required
