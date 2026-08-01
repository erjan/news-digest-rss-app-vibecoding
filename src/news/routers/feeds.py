from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..crud import create_feed, delete_feed, get_feed, list_feeds
from ..database import get_db
from ..schemas import FeedCreate, FeedRead
from ..services.fetch_service import fetch_and_save

router = APIRouter(prefix="/feeds", tags=["feeds"])

DbDep = Annotated[AsyncSession, Depends(get_db)]


@router.post("/", response_model=FeedRead, status_code=201)
async def create_feed_endpoint(data: FeedCreate, db: DbDep):
    """Create a new RSS feed."""
    return await create_feed(db, data)


@router.get("/", response_model=list[FeedRead])
async def list_feeds_endpoint(db: DbDep, active_only: bool = True):
    """List all feeds."""
    return await list_feeds(db, active_only=active_only)


@router.delete("/{feed_id}", status_code=204)
async def delete_feed_endpoint(feed_id: int, db: DbDep):
    """Delete a feed by ID."""
    success = await delete_feed(db, feed_id)
    if not success:
        raise HTTPException(status_code=404, detail="Feed not found")


@router.post("/{feed_id}/fetch")
async def fetch_feed_endpoint(feed_id: int, db: DbDep):
    """Manually trigger RSS fetch for a specific feed."""
    feed = await get_feed(db, feed_id)
    if feed is None:
        raise HTTPException(status_code=404, detail="Feed not found")

    new_count = await fetch_and_save(db, feed)
    return {"message": f"Fetched {new_count} new articles", "new_articles_count": new_count}
