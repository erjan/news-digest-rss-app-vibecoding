FROM python:3.13-slim AS builder

WORKDIR /app

ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN pip install --upgrade pip uv

COPY pyproject.toml uv.lock README.md ./
COPY src ./src

RUN uv sync --frozen --no-dev


FROM python:3.13-slim AS runtime

WORKDIR /app

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN useradd -m -u 1000 app

COPY --from=builder /app/.venv /app/.venv
COPY src ./src
COPY alembic.ini ./alembic.ini
COPY alembic ./alembic

USER app

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=3s --start-period=20s --retries=3 CMD python -c "import os, sys, urllib.request; port = os.getenv('PORT', '8000'); urllib.request.urlopen(f'http://127.0.0.1:{port}/health', timeout=2); sys.exit(0)"

CMD ["sh", "-c", "alembic upgrade head && exec uvicorn src.news.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
