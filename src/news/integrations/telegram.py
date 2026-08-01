import httpx

from ..log import log
from .. import settings as settings_module


async def notify_new_articles(article_count: int, feed_title: str) -> None:
    """Send a Telegram notification about newly fetched articles."""
    token = settings_module.settings.telegram_bot_token
    chat_id = settings_module.settings.telegram_chat_id
    if not token or not chat_id:
        log.info(
            "telegram_notification_skipped",
            reason="missing_credentials",
            article_count=article_count,
            feed_title=feed_title,
        )
        return

    message = f"New articles fetched: {article_count}\nSource: {feed_title}"
    url = f"https://api.telegram.org/bot{token}/sendMessage"

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            url,
            json={"chat_id": chat_id, "text": message, "disable_web_page_preview": True},
        )
        response.raise_for_status()
        log.info(
            "telegram_notification_sent",
            article_count=article_count,
            feed_title=feed_title,
            status_code=response.status_code,
        )
