import importlib
import sys
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from testcontainers.community.postgres import PostgresContainer

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture(scope="session")
def pg():
    with PostgresContainer(
        "postgres:16-alpine",
        username="postgres",
        password="postgres",
        dbname="news_digest",
    ) as container:
        yield container


@pytest_asyncio.fixture()
async def app(pg, monkeypatch):
    port = pg.get_exposed_port(5432)
    host = pg.get_container_host_ip()
    monkeypatch.setenv(
        "DATABASE_URL",
        f"postgresql+asyncpg://postgres:postgres@{host}:{port}/news_digest",
    )
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("GEMINI_API_KEY", "")
    monkeypatch.setenv("GOOGLE_API_KEY", "")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "")

    from src.news import database, main, models, settings

    importlib.reload(settings)
    importlib.reload(database)
    importlib.reload(models)
    importlib.reload(main)

    async with database.engine.begin() as conn:
        await conn.run_sync(database.Base.metadata.create_all)

    application = main.create_app()
    yield application

    async with database.engine.begin() as conn:
        await conn.run_sync(database.Base.metadata.drop_all)


@pytest_asyncio.fixture()
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as http_client:
        yield http_client
