# News Digest API

FastAPI service that:
- stores RSS feeds
- fetches new articles
- generates article summaries (Gemini + local fallback)
- sends Telegram notifications for new articles

## Tech Stack

- FastAPI
- SQLAlchemy (async) + PostgreSQL
- Alembic
- APScheduler
- Gemini API
- Prometheus metrics + OpenTelemetry tracing
- Docker / Docker Compose

## Project Structure

- `src/news/main.py` — app startup, routers, scheduler
- `src/news/routers/` — API endpoints
- `src/news/services/` — fetch/summarize business logic
- `src/news/integrations/` — Gemini + Telegram integrations
- `alembic/` — DB migrations
- `monitoring/` — Prometheus + Alertmanager configs

## Environment Variables

Create `.env` in project root:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost/news_digest

GEMINI_API_KEY=
GOOGLE_API_KEY=

TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

OTEL_ENABLED=false
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
OTEL_EXPORTER_OTLP_INSECURE=true
OTEL_SERVICE_NAME=news-digest-api
```

## Run Locally (without Docker)

```bash
uv sync
uv run alembic upgrade head
uv run uvicorn src.news.main:app --host 127.0.0.1 --port 8000
```

Health check:
- `GET http://127.0.0.1:8000/health`

## Run with Docker Compose

```bash
docker compose up -d --build
```

Default services:
- API: `127.0.0.1:8000`
- Prometheus: `127.0.0.1:9090`
- Alertmanager: `127.0.0.1:9093`

## Main API Endpoints

- `POST /feeds/` — add RSS feed
- `GET /feeds/` — list feeds
- `POST /feeds/{feed_id}/fetch` — fetch new articles for feed
- `GET /articles/` — list articles
- `GET /articles/{article_id}` — article details
- `POST /articles/{article_id}/summarize` — generate/update summary
- `GET /metrics` — Prometheus metrics

## Scheduler

- Every 1 hour: fetches active feeds
- Every 10 minutes: summarizes pending articles

## CI/CD

`push` to `main` triggers GitHub Actions deploy workflow:
- build + push image to GHCR
- SSH to server
- `docker compose pull app`
- `docker compose up -d --no-deps app`

Workflow file:
- `.github/workflows/deploy.yml`

## CI Smoke Test

This line is another tiny non-functional change to trigger CI/CD validation.
#sldjf trigger small build