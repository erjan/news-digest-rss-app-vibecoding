import asyncio
from datetime import UTC, datetime
from typing import Any

import feedparser


def build_article_payload(entry: Any) -> dict[str, Any]:
    """Normalize a feedparser entry into the internally-used article payload."""
    content = entry.get("description") or ""
    if hasattr(entry, "content") and entry.content:
        content = entry.content[0].value if isinstance(entry.content, list) else entry.content

    published = entry.get("published_parsed")
    if published:
        year, month, day, hour, minute, second = published[:6]
        published_dt = datetime(year, month, day, hour, minute, second, tzinfo=UTC)
    else:
        published_dt = datetime.now(UTC)

    return {
        "url": entry.get("link", ""),
        "title": entry.get("title", ""),
        "content": content,
        "published_at": published_dt,
    }


async def fetch_feed(url: str) -> list[dict[str, Any]]:
    """Parse RSS feed and return list of articles as dictionaries."""

    def _parse() -> list[dict[str, Any]]:
        try:
            feed = feedparser.parse(url)
            return [build_article_payload(entry) for entry in feed.entries]
        except (AttributeError, TypeError, ValueError):
            return []

    return await asyncio.to_thread(_parse)
