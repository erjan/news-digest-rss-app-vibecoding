from datetime import UTC, datetime

import pytest

from src.news.services import rss_fetcher


class FakeContent:
    def __init__(self, value: str):
        self.value = value


class FakeEntry:
    def __init__(self):
        self.content = [FakeContent("Полный текст новости")]
        self.published_parsed = (2026, 8, 1, 12, 30, 0)

    def get(self, key, default=None):
        values = {
            "link": "https://example.com/news/1",
            "title": "Пример новости",
            "description": "Короткое описание",
            "published_parsed": (2026, 8, 1, 12, 30, 0),
        }
        return values.get(key, default)


@pytest.mark.asyncio
async def test_fetch_feed_returns_article_payload(monkeypatch):
    class FakeFeed:
        def __init__(self):
            self.entries = [FakeEntry()]

    monkeypatch.setattr(rss_fetcher.feedparser, "parse", lambda _: FakeFeed())

    articles = await rss_fetcher.fetch_feed("https://example.com/rss")

    assert len(articles) == 1
    assert articles[0]["url"] == "https://example.com/news/1"
    assert articles[0]["title"] == "Пример новости"
    assert articles[0]["content"] == "Полный текст новости"
    assert articles[0]["published_at"] == datetime(2026, 8, 1, 12, 30, 0, tzinfo=UTC)