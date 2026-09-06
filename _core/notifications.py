import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def send_telegram_notification(message: str) -> None:

    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
        return

    try:
        requests.post(
            f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
            json={
                "chat_id": settings.TELEGRAM_CHAT_ID,
                "text": message,
                "parse_mode": "HTML",
            },
            timeout=5,
        )
    except requests.RequestException:
        logger.warning("Failed to send Telegram notification", exc_info=True)
