import asyncio
import re

from google import genai
from google.genai.errors import ClientError, ServerError

from ..log import log
from ..settings import settings

SYSTEM_PROMPT = (
    "Ты — редактор новостного дайджеста. "
    "Пиши краткие саммари новостей на русском языке: 3–4 предложения, "
    "только ключевые факты, без воды и субъективных оценок."
)


def build_local_summary(title: str, content: str) -> str:
    cleaned_content = re.sub(r"\s+", " ", content).strip()
    if not cleaned_content:
        return f"{title}: summary unavailable."

    preview = cleaned_content[:320]
    if "." in preview:
        sentences = re.split(r"(?<=[.!?])\s+", preview)
        preview = " ".join(sentences[:2]).strip()

    return f"{title}. {preview}"


async def summarize_with_gemini(title: str, content: str) -> str:
    api_key = settings.gemini_api_key or settings.google_api_key
    if not api_key:
        raise RuntimeError("Gemini API key not configured")

    client = genai.Client(api_key=api_key)
    prompt = f"{SYSTEM_PROMPT}\n\nЗаголовок: {title}\n\nТекст:\n{content[:3000]}"

    def _generate() -> str:
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt,
        )
        return (response.text or "").strip()

    return await asyncio.to_thread(_generate)


async def summarize_article(title: str, content: str) -> str:
    if not title and not content:
        return "No content available"

    if settings.gemini_api_key or settings.google_api_key:
        try:
            return await summarize_with_gemini(title, content)
        except (ClientError, ServerError, RuntimeError) as exc:
            log.warning("gemini_summary_failed", error=str(exc), fallback="local_summary")
            return build_local_summary(title, content)

    log.info("gemini_summary_skipped", reason="missing_api_key", fallback="local_summary")
    return build_local_summary(title, content)
