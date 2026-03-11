from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.api.routes import app

client = TestClient(app)


class TestGetPrices:
    def test_returns_200(self):
        response = client.get("/prices")
        assert response.status_code == 200

    def test_response_has_prices_key(self):
        response = client.get("/prices")
        assert "prices" in response.json()

    def test_prices_is_list(self):
        response = client.get("/prices")
        assert isinstance(response.json()["prices"], list)


class TestGetCurves:
    def test_returns_200(self):
        response = client.get("/curves")
        assert response.status_code == 200

    def test_response_has_expected_keys(self):
        data = client.get("/curves").json()
        assert "bootstrapped" in data
        assert "forward_rates" in data
        assert "swap_rates" in data

    def test_custom_maturity_range(self):
        response = client.get("/curves?maturity_start=1&maturity_end=5&num_points=5")
        assert response.status_code == 200


class TestBuildCustomCurve:
    def test_valid_data_returns_200(self):
        payload = {
            "market_data": [
                {"maturity": 1, "rate": 0.02},
                {"maturity": 2, "rate": 0.025},
                {"maturity": 3, "rate": 0.03},
            ]
        }
        response = client.post("/curves/custom", json=payload)
        assert response.status_code == 200

    def test_empty_data_returns_400(self):
        response = client.post("/curves/custom", json={"market_data": []})
        assert response.status_code == 400

    def test_response_structure(self):
        payload = {
            "market_data": [
                {"maturity": 1, "rate": 0.02},
                {"maturity": 3, "rate": 0.04},
            ]
        }
        data = client.post("/curves/custom", json=payload).json()
        assert "bootstrapped" in data
        assert "forward_rates" in data
        assert "swap_rates" in data


class TestGetSpreads:
    def test_returns_200(self):
        response = client.get("/spreads")
        assert response.status_code == 200

    def test_response_has_spreads_key(self):
        assert "spreads" in client.get("/spreads").json()


class TestSendMessage:
    def test_unknown_channel_returns_400(self):
        response = client.post("/messages", json={"text": "hello", "channel": "fax"})
        assert response.status_code == 400

    def test_sms_without_to_number_returns_400(self):
        response = client.post("/messages", json={"text": "hello", "channel": "sms"})
        assert response.status_code == 400

    def test_telegram_success(self):
        with patch(
            "backend.api.routes.telegram.send_message",
            new_callable=AsyncMock,
            return_value=True,
        ):
            response = client.post("/messages", json={"text": "hello", "channel": "telegram"})
        assert response.status_code == 200
        assert response.json()["channel"] == "telegram"

    def test_telegram_failure_returns_502(self):
        with patch(
            "backend.api.routes.telegram.send_message",
            new_callable=AsyncMock,
            return_value=False,
        ):
            response = client.post("/messages", json={"text": "hello", "channel": "telegram"})
        assert response.status_code == 502


class TestSendPriceAlert:
    def test_unknown_channel_returns_400(self):
        payload = {
            "contract": "GASOLINE",
            "price": 120.0,
            "threshold": 100.0,
            "direction": "ABOVE",
            "channel": "email",
        }
        response = client.post("/alerts/price", json=payload)
        assert response.status_code == 400

    def test_telegram_price_alert_success(self):
        payload = {
            "contract": "GASOLINE",
            "price": 120.0,
            "threshold": 100.0,
            "direction": "ABOVE",
            "channel": "telegram",
        }
        with patch(
            "backend.api.routes.telegram.send_price_alert",
            new_callable=AsyncMock,
            return_value=True,
        ):
            response = client.post("/alerts/price", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["contract"] == "GASOLINE"
        assert data["alert"] == "sent"

    def test_sms_price_alert_requires_to_number(self):
        payload = {
            "contract": "GASOLINE",
            "price": 120.0,
            "threshold": 100.0,
            "direction": "ABOVE",
            "channel": "sms",
        }
        response = client.post("/alerts/price", json=payload)
        assert response.status_code == 400
