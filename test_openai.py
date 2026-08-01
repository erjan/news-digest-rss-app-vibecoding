import pytest

from src.news.integrations import openai_client


@pytest.mark.asyncio
async def test_summarize_article_returns_local_fallback_when_gemini_missing(monkeypatch):
    monkeypatch.setattr(openai_client.settings, "gemini_api_key", "")
    monkeypatch.setattr(openai_client.settings, "google_api_key", "")

    summary = await openai_client.summarize_article("Test Title", "Test content")

    assert summary.startswith("Test Title.")