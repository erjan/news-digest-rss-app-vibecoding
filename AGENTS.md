# [AGENTS.md](http://AGENTS.md)

## Проект

Smart News Digest - агрегатор RSS с AI-summary.

## Стек

- Python 3.12, uv

- FastAPI 0.110 async, Pydantic v2

- SQLAlchemy 2.0 async, asyncpg, PostgreSQL 16

- OpenAI gpt-4o-mini для summary

- APScheduler для cron

## Стиль

- Async везде где I/O

- Type hints везде

- response_model на всех endpoints

- snake_case в Python, camelCase в API ответах

## Структура

- src/news/routers - HTTP endpoints

- src/news/services - бизнес-логика

- src/news/crud - доступ к БД

- src/news/integrations - внешние API

- src/news/tasks - cron-задачи

## Команды

- uv sync - установить

- uv run alembic upgrade head - миграции

- uv run fastapi dev src/news/[main.py](http://main.py) - dev-сервер

- uv run pytest - тесты

- uv run ruff check . && uv run mypy src - проверки

## Чего не делать

- Не блокирующие вызовы в async-коде

- Не f-string в SQL (только параметры)

- Не хардкод OpenAI-ключа

