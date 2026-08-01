import pytest

from src.news.services.fetch_service import summarize_pending


@pytest.mark.asyncio
async def test_summarize_pending_processes_articles(monkeypatch):
    class FakeArticle:
        def __init__(self, article_id: int, title: str, content: str, summary: str | None):
            self.id = article_id
            self.title = title
            self.content = content
            self.summary = summary

    articles = [FakeArticle(1, "Заголовок", "Контент", None)]

    async def fake_list_articles(db, limit=5):
        return articles

    async def fake_summarize_article(title: str, content: str) -> str:
        return f"Summary for {title}"

    async def fake_update_article_summary(db, article_id: int, summary: str) -> None:
        articles[0].summary = summary

    monkeypatch.setattr("src.news.services.fetch_service.list_articles", fake_list_articles)
    monkeypatch.setattr("src.news.services.fetch_service.summarize_article", fake_summarize_article)
    monkeypatch.setattr(
        "src.news.services.fetch_service.update_article_summary",
        fake_update_article_summary,
    )

    processed = await summarize_pending(db=None, batch_size=5)

    assert processed == 1
    assert articles[0].summary == "Summary for Заголовок"