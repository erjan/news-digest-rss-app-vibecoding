from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from ..crud import (
    create_article,
    find_article_by_url,
    list_articles,
    update_article_summary,
)
from ..integrations.openai_client import summarize_article
from ..integrations.telegram import notify_new_articles
from ..log import log
from ..models import Feed
from ..services.rss_fetcher import fetch_feed


async def fetch_and_save(db: AsyncSession, feed: Feed) -> int:
    """Fetch articles from RSS feed and save new ones to database."""
    log.info("feed_fetch_started", feed_id=feed.id, feed_title=feed.title, feed_url=feed.url)
    articles_data = await fetch_feed(feed.url)
    new_count = 0

    for article_data in articles_data:
        existing = await find_article_by_url(db, article_data["url"])
        if existing is None:
            await create_article(db, feed.id, article_data)
            new_count += 1

    feed.last_fetched = datetime.now(UTC)
    await db.commit()
    log.info(
        "feed_fetch_completed",
        feed_id=feed.id,
        feed_title=feed.title,
        fetched_count=len(articles_data),
        new_articles_count=new_count,
    )

    if new_count > 0:
        await notify_new_articles(new_count, feed.title)

    return new_count


async def summarize_pending(db: AsyncSession, batch_size: int = 5) -> int:
    """Summarize articles that don't have a summary yet."""
    articles = await list_articles(db, limit=batch_size)
    pending = [a for a in articles if a.summary is None]
    processed = 0

    log.info("summary_batch_started", batch_size=batch_size, pending_count=len(pending))

    for article in pending:
        summary = await summarize_article(article.title, article.content)
        await update_article_summary(db, article.id, summary)
        processed += 1
        log.info("article_summarized", article_id=article.id, feed_id=article.feed_id)

    return processed
