import logging
from typing import Optional

from backend.config import config

logger = logging.getLogger(__name__)


class TelegramService:
    """Send notifications to a Telegram chat via the Bot API."""

    def __init__(
        self,
        api_token: Optional[str] = None,
        chat_id: Optional[str] = None,
    ) -> None:
        self.api_token = api_token or config.telegram_api_token
        self.chat_id = chat_id or config.telegram_chat_id

    def _is_configured(self) -> bool:
        return bool(self.api_token and self.chat_id)

    async def send_message(self, text: str) -> bool:
        """Send *text* to the configured Telegram chat.

        Returns True on success, False otherwise.
        """
        if not self._is_configured():
            logger.warning("Telegram credentials not configured – message skipped.")
            return False

        try:
            from telegram import Bot  # python-telegram-bot

            bot = Bot(token=self.api_token)
            await bot.send_message(chat_id=self.chat_id, text=text)
            logger.info("Telegram message sent successfully.")
            return True
        except Exception as exc:
            logger.error("Failed to send Telegram message: %s", exc)
            return False

    async def send_price_alert(self, contract: str, price: float, threshold: float, direction: str) -> bool:
        """Convenience method: send a formatted price-alert message."""
        emoji = "📈" if direction.upper() == "ABOVE" else "📉"
        text = (
            f"{emoji} *Price Alert* – {contract}\n"
            f"Current price: *{price:.4f}*\n"
            f"Threshold ({direction}): *{threshold:.4f}*"
        )
        return await self.send_message(text)
