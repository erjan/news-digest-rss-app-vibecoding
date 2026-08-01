from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Article, Feed
from .schemas import FeedCreate


async def create_feed(db: AsyncSession, data: FeedCreate) -> Feed:
    feed = Feed(url=str(data.url), title=data.title)
    db.add(feed)
    await db.commit()
    await db.refresh(feed)
    return feed


async def list_feeds(db: AsyncSession, active_only: bool = True) -> list[Feed]:
    stmt = select(Feed)
    if active_only:
        stmt = stmt.where(Feed.is_active.is_(True))
    result = await db.scalars(stmt)
    return list(result.all())


async def get_feed(db: AsyncSession, feed_id: int) -> Feed | None:
    return await db.get(Feed, feed_id)


async def get_article_by_id(db: AsyncSession, article_id: int) -> Article | None:
    return await db.get(Article, article_id)


async def delete_feed(db: AsyncSession, feed_id: int) -> bool:
    feed = await get_feed(db, feed_id)
    if feed is None:
        return False
    await db.execute(delete(Article).where(Article.feed_id == feed_id))
    await db.delete(feed)
    await db.commit()
    return True


async def create_article(db: AsyncSession, feed_id: int, data: dict) -> Article:
    article = Article(feed_id=feed_id, **data)
    db.add(article)
    await db.commit()
    await db.refresh(article)
    return article


async def list_articles(
    db: AsyncSession,
    feed_id: int | None = None,
    limit: int = 50,
) -> list[Article]:
    stmt = select(Article).limit(limit)
    if feed_id is not None:
        stmt = stmt.where(Article.feed_id == feed_id)
    result = await db.scalars(stmt)
    return list(result.all())


async def find_article_by_url(db: AsyncSession, url: str) -> Article | None:
    stmt = select(Article).where(Article.url == url)
    return await db.scalar(stmt)


async def update_article_summary(
    db: AsyncSession,
    article_id: int,
    summary: str,
) -> None:
    article = await db.get(Article, article_id)
    if article is None:
        return
    article.summary = summary
    await db.commit()
