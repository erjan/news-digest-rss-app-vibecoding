from datetime import UTC, datetime

from hypothesis import given
from hypothesis import strategies as st

from src.news.services.rss_fetcher import build_article_payload


@given(
    url=st.text(min_size=1, max_size=200),
    title=st.text(min_size=1, max_size=120),
    description=st.text(min_size=0, max_size=300),
    content=st.text(min_size=0, max_size=500),
)
def test_build_article_payload_preserves_generated_fields(url, title, description, content):
    class FakeContent:
        def __init__(self, value: str):
            self.value = value

    class FakeEntry:
        def __init__(self):
            self.content = [FakeContent(content)]
            self.published_parsed = (2026, 8, 1, 12, 30, 0)

        def get(self, key, default=None):
            values = {
                "link": url,
                "title": title,
                "description": description,
                "published_parsed": (2026, 8, 1, 12, 30, 0),
            }
            return values.get(key, default)

    payload = build_article_payload(FakeEntry())

    assert payload["url"] == url
    assert payload["title"] == title
    assert payload["content"] == content
    assert payload["published_at"] == datetime(2026, 8, 1, 12, 30, 0, tzinfo=UTC)
