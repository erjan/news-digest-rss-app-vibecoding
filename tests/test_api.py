from datetime import UTC, datetime

import pytest


@pytest.mark.asyncio
async def test_health_check(client):
    response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@pytest.mark.asyncio
async def test_feeds_endpoint_returns_list(client):
    response = await client.get("/feeds/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_can_create_and_list_feed(client):
    create_response = await client.post(
        "/feeds/",
        json={"url": "https://example.com/rss.xml", "title": "Example Feed"},
    )

    assert create_response.status_code == 201
    created_feed = create_response.json()
    assert created_feed["title"] == "Example Feed"

    list_response = await client.get("/feeds/")
    assert list_response.status_code == 200
    assert any(feed["id"] == created_feed["id"] for feed in list_response.json())


@pytest.mark.asyncio
async def test_can_delete_feed(client):
    create_response = await client.post(
        "/feeds/",
        json={"url": "https://example.com/rss.xml", "title": "Delete Me"},
    )
    feed_id = create_response.json()["id"]

    delete_response = await client.delete(f"/feeds/{feed_id}")

    assert delete_response.status_code == 204

    list_response = await client.get("/feeds/")
    assert list_response.status_code == 200
    assert all(feed["id"] != feed_id for feed in list_response.json())


@pytest.mark.asyncio
async def test_can_delete_feed_with_articles(client, monkeypatch):
    async def fake_fetch_feed(url: str):
        return [
            {
                "url": "https://example.com/news/1",
                "title": "Example Article",
                "content": "Body text",
                "published_at": datetime(2026, 8, 1, 12, 30, tzinfo=UTC),
            }
        ]

    monkeypatch.setattr("src.news.services.fetch_service.fetch_feed", fake_fetch_feed)

    create_response = await client.post(
        "/feeds/",
        json={"url": "https://example.com/rss.xml", "title": "Delete With Articles"},
    )
    feed_id = create_response.json()["id"]

    fetch_response = await client.post(f"/feeds/{feed_id}/fetch")
    assert fetch_response.status_code == 200

    delete_response = await client.delete(f"/feeds/{feed_id}")
    assert delete_response.status_code == 204

    feeds_response = await client.get("/feeds/")
    assert all(feed["id"] != feed_id for feed in feeds_response.json())

    articles_response = await client.get("/articles/", params={"feed_id": feed_id, "limit": 10})
    assert articles_response.status_code == 200
    assert articles_response.json() == []


@pytest.mark.asyncio
async def test_can_fetch_and_list_articles(client, monkeypatch):
    async def fake_fetch_feed(url: str):
        return [
            {
                "url": "https://example.com/news/1",
                "title": "Example Article",
                "content": "Body text",
                "published_at": datetime(2026, 8, 1, 12, 30, tzinfo=UTC),
            }
        ]

    monkeypatch.setattr("src.news.services.fetch_service.fetch_feed", fake_fetch_feed)

    create_response = await client.post(
        "/feeds/",
        json={"url": "https://example.com/rss.xml", "title": "Article Feed"},
    )
    feed_id = create_response.json()["id"]

    fetch_response = await client.post(f"/feeds/{feed_id}/fetch")
    assert fetch_response.status_code == 200
    assert fetch_response.json()["new_articles_count"] == 1

    list_articles_response = await client.get("/articles/", params={"feed_id": feed_id, "limit": 10})
    assert list_articles_response.status_code == 200
    articles = list_articles_response.json()
    assert len(articles) == 1
    assert articles[0]["title"] == "Example Article"

    article_id = articles[0]["id"]
    detail_response = await client.get(f"/articles/{article_id}")
    assert detail_response.status_code == 200
    assert detail_response.json()["title"] == "Example Article"

    summarize_response = await client.post(f"/articles/{article_id}/summarize")
    assert summarize_response.status_code == 200
    assert summarize_response.json()["article_id"] == article_id
    assert summarize_response.json()["summary"]
    assert not summarize_response.json()["summary"].startswith("[TEST SUMMARY]")
