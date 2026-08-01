from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field, field_serializer


class FeedCreate(BaseModel):
    url: str = Field(min_length=1)
    title: str = Field(min_length=1)


class FeedRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    url: str
    title: str
    last_fetched: datetime | None
    is_active: bool
    created_at: datetime

    @field_serializer("last_fetched", when_used="always")
    @field_serializer("created_at", when_used="always")
    def serialize_datetime(self, value: datetime | None) -> str | None:
        if value is None:
            return None
        if value.tzinfo is None:
            value = value.replace(tzinfo=UTC)
        return value.isoformat()


class ArticleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    feed_id: int
    title: str
    url: str
    summary: str | None
    published_at: datetime

    @field_serializer("published_at", when_used="always")
    def serialize_published_at(self, value: datetime) -> str:
        if value.tzinfo is None:
            value = value.replace(tzinfo=UTC)
        return value.isoformat()


class ArticleSummaryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    article_id: int
    summary: str


class ArticleSearchQuery(BaseModel):
    query: str
    limit: int = Field(default=10, le=50)
