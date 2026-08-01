import pytest
from sqlalchemy import select

from src.news.database import async_session_maker
from src.news.models import Feed


@pytest.mark.asyncio
async def test_database_session_can_read_feeds():
    async with async_session_maker() as db:
        result = await db.execute(select(Feed))
        feeds = result.scalars().all()

    assert isinstance(feeds, list)
    assert len(feeds) >= 0