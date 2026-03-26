import logging
from typing import Optional

from backend.config import config

logger = logging.getLogger(__name__)


class TwilioService:
    """Send SMS notifications via the Twilio REST API."""

    def __init__(
        self,
        account_sid: Optional[str] = None,
        auth_token: Optional[str] = None,
        from_number: Optional[str] = None,
    ) -> None:
        self.account_sid = account_sid or config.twilio_account_sid
        self.auth_token = auth_token or config.twilio_auth_token
        self.from_number = from_number or config.twilio_phone_number

    def _is_configured(self) -> bool:
        return bool(self.account_sid and self.auth_token and self.from_number)

    def send_sms(self, to_number: str, body: str) -> bool:
        """Send an SMS to *to_number* with the given *body*.

        Returns True on success, False otherwise.
        """
        if not self._is_configured():
            logger.warning("Twilio credentials not configured – SMS skipped.")
            return False

        try:
            from twilio.rest import Client  # twilio

            client = Client(self.account_sid, self.auth_token)
            message = client.messages.create(
                body=body,
                from_=self.from_number,
                to=to_number,
            )
            logger.info("SMS sent. SID: %s", message.sid)
            return True
        except Exception as exc:
            logger.error("Failed to send SMS: %s", exc)
            return False

    def send_price_alert(self, to_number: str, contract: str, price: float, threshold: float, direction: str) -> bool:
        """Convenience method: send a formatted price-alert SMS."""
        body = (
            f"[GasolineBroker] Price Alert – {contract}: "
            f"current price {price:.4f} is {direction} threshold {threshold:.4f}."
        )
        return self.send_sms(to_number, body)
