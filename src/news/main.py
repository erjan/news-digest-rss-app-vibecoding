from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI

from .crud import list_feeds
from .database import async_session_maker, engine
from .log import configure_logging, log
from .metrics import configure_metrics
from .routers import articles, feeds
from .services.fetch_service import fetch_and_save, summarize_pending
from .telemetry import configure_tracing

scheduler = AsyncIOScheduler()


def initialize_scheduler() -> None:
    """Register and start background jobs once per app lifecycle."""
    if scheduler.running:
        return

    scheduler.add_job(fetch_all_feeds, "interval", hours=1, replace_existing=True)
    scheduler.add_job(summarize_articles, "interval", minutes=10, replace_existing=True)
    scheduler.start()
    log.info("scheduler_started", fetch_interval_hours=1, summarize_interval_minutes=10)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events for the app."""
    configure_logging()
    log.info("app_starting", app_name="News Digest API", version="1.0")
    initialize_scheduler()
    yield
    log.info("app_stopping")
    scheduler.shutdown(wait=False)


def create_app() -> FastAPI:
    app = FastAPI(title="News Digest API railway edition! ha 1234 added to signal change", version="1.0", lifespan=lifespan)
    configure_tracing(app, engine)
    configure_metrics(app)
    app.include_router(feeds.router)
    app.include_router(articles.router)

    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy"}

    return app


app = create_app()


async def fetch_all_feeds():
    """Background task: fetch articles from all active feeds."""
    async with async_session_maker() as db:
        active_feeds = await list_feeds(db, active_only=True)
        log.info("feed_fetch_cycle_started", active_feed_count=len(active_feeds))
        for feed in active_feeds:
            await fetch_and_save(db, feed)
        log.info("feed_fetch_cycle_finished", active_feed_count=len(active_feeds))


async def summarize_articles():
    """Background task: summarize pending articles."""
    async with async_session_maker() as db:
        processed = await summarize_pending(db, batch_size=5)
        log.info("summary_batch_finished", batch_size=5, processed=processed)
