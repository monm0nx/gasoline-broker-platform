from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.services.notifications.telegram_service import TelegramService
from backend.services.notifications.twilio_service import TwilioService


# ── TelegramService ──────────────────────────────────────────────────────────

class TestTelegramServiceConfiguration:
    def test_not_configured_when_credentials_missing(self):
        svc = TelegramService(api_token="", chat_id="")
        assert not svc._is_configured()

    def test_configured_when_credentials_present(self):
        svc = TelegramService(api_token="tok", chat_id="123")
        assert svc._is_configured()


class TestTelegramSendMessage:
    @pytest.mark.asyncio
    async def test_returns_false_when_not_configured(self):
        svc = TelegramService(api_token="", chat_id="")
        result = await svc.send_message("hello")
        assert result is False

    @pytest.mark.asyncio
    async def test_sends_message_successfully(self):
        svc = TelegramService(api_token="tok", chat_id="123")
        mock_bot = AsyncMock()
        mock_bot.send_message = AsyncMock()
        with patch("telegram.Bot", return_value=mock_bot):
            result = await svc.send_message("test message")
        assert result is True
        mock_bot.send_message.assert_awaited_once_with(chat_id="123", text="test message")

    @pytest.mark.asyncio
    async def test_returns_false_on_exception(self):
        svc = TelegramService(api_token="tok", chat_id="123")
        with patch("telegram.Bot", side_effect=Exception("network error")):
            result = await svc.send_message("test message")
        assert result is False


class TestTelegramSendPriceAlert:
    @pytest.mark.asyncio
    async def test_sends_alert_with_correct_emoji_above(self):
        svc = TelegramService(api_token="tok", chat_id="123")
        mock_bot = AsyncMock()
        mock_bot.send_message = AsyncMock()
        with patch("telegram.Bot", return_value=mock_bot):
            result = await svc.send_price_alert("GASOLINE", 120.0, 100.0, "ABOVE")
        assert result is True
        call_text = mock_bot.send_message.call_args[1]["text"]
        assert "📈" in call_text
        assert "GASOLINE" in call_text

    @pytest.mark.asyncio
    async def test_sends_alert_with_correct_emoji_below(self):
        svc = TelegramService(api_token="tok", chat_id="123")
        mock_bot = AsyncMock()
        mock_bot.send_message = AsyncMock()
        with patch("telegram.Bot", return_value=mock_bot):
            result = await svc.send_price_alert("GASOLINE", 80.0, 100.0, "BELOW")
        assert result is True
        call_text = mock_bot.send_message.call_args[1]["text"]
        assert "📉" in call_text


# ── TwilioService ────────────────────────────────────────────────────────────

class TestTwilioServiceConfiguration:
    def test_not_configured_when_credentials_missing(self):
        svc = TwilioService(account_sid="", auth_token="", from_number="")
        assert not svc._is_configured()

    def test_configured_when_credentials_present(self):
        svc = TwilioService(account_sid="AC123", auth_token="auth", from_number="+1555")
        assert svc._is_configured()


class TestTwilioSendSms:
    def test_returns_false_when_not_configured(self):
        svc = TwilioService(account_sid="", auth_token="", from_number="")
        result = svc.send_sms("+15550001111", "hello")
        assert result is False

    def test_sends_sms_successfully(self):
        svc = TwilioService(account_sid="AC123", auth_token="auth", from_number="+1555")
        mock_message = MagicMock()
        mock_message.sid = "SM123"
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_message

        with patch("twilio.rest.Client", return_value=mock_client):
            result = svc.send_sms("+15550001111", "test body")

        assert result is True
        mock_client.messages.create.assert_called_once_with(
            body="test body",
            from_="+1555",
            to="+15550001111",
        )

    def test_returns_false_on_exception(self):
        svc = TwilioService(account_sid="AC123", auth_token="auth", from_number="+1555")
        with patch("twilio.rest.Client", side_effect=Exception("api error")):
            result = svc.send_sms("+15550001111", "test")
        assert result is False


class TestTwilioSendPriceAlert:
    def test_sends_alert_with_formatted_body(self):
        svc = TwilioService(account_sid="AC123", auth_token="auth", from_number="+1555")
        mock_message = MagicMock()
        mock_message.sid = "SM123"
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_message

        with patch("twilio.rest.Client", return_value=mock_client):
            result = svc.send_price_alert("+15550001111", "GASOLINE", 120.0, 100.0, "ABOVE")

        assert result is True
        body = mock_client.messages.create.call_args[1]["body"]
        assert "GASOLINE" in body
        assert "ABOVE" in body
        assert "120" in body
