from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..crud import get_article_by_id, list_articles, update_article_summary
from ..database import get_db
from ..integrations.openai_client import summarize_article
from ..schemas import ArticleRead, ArticleSummaryRead

router = APIRouter(prefix="/articles", tags=["articles"])

DbDep = Annotated[AsyncSession, Depends(get_db)]


@router.get("/", response_model=list[ArticleRead])
async def list_articles_endpoint(
    db: DbDep,
    feed_id: int | None = None,
    limit: int = 50,
    offset: int = 0,
):
    """List articles with pagination and optional feed filter."""
    articles = await list_articles(db, feed_id=feed_id, limit=limit)
    return articles[offset : offset + limit]


@router.post("/test")
async def test_endpoint():
    """Test endpoint."""
    return {"message": "Test works"}


@router.get("/{article_id}", response_model=ArticleRead)
async def get_article_endpoint(article_id: int, db: DbDep):
    """Get article details by ID."""
    article = await get_article_by_id(db, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.post("/{article_id}/summarize", response_model=ArticleSummaryRead)
async def summarize_article_endpoint(article_id: int, db: DbDep):
    """Manually trigger summary generation for an article."""
    article = await get_article_by_id(db, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")

    summary = await summarize_article(article.title, article.content)
    await update_article_summary(db, article.id, summary)
    return {"article_id": article.id, "summary": summary}
