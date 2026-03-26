import logging
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from backend.services.market_data.data_aggregator import MarketDataAggregator
from backend.services.curve_builder.curve_builder import CurveBuilder
from backend.services.notifications.telegram_service import TelegramService
from backend.services.notifications.twilio_service import TwilioService

logger = logging.getLogger(__name__)
app = FastAPI(title="Gasoline Broker Platform API", version="0.1.0")

aggregator = MarketDataAggregator()
telegram = TelegramService()
twilio = TwilioService()


# ── Request / Response models ────────────────────────────────────────────────

class MessageRequest(BaseModel):
    text: str
    channel: str = "telegram"       # "telegram" | "sms"
    to_number: Optional[str] = None  # required when channel == "sms"


class AlertRequest(BaseModel):
    contract: str
    price: float
    threshold: float
    direction: str = "ABOVE"        # "ABOVE" | "BELOW"
    channel: str = "telegram"
    to_number: Optional[str] = None


class CurveRequest(BaseModel):
    market_data: list  # [{"maturity": float, "rate": float}, ...]


# ── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/prices")
async def get_prices():
    """Return the latest normalised market prices from all configured sources."""
    aggregator.fetch_data()
    prices = aggregator.normalize_data()
    return {"prices": prices}


@app.get("/curves")
async def get_curves(
    maturity_start: float = 1.0,
    maturity_end: float = 10.0,
    num_points: int = 10,
):
    """Build and return a bootstrapped curve over the requested maturity range."""
    import numpy as np

    maturities = list(np.linspace(maturity_start, maturity_end, num_points))
    sample_data = [
        {"maturity": t, "rate": 0.02 + 0.003 * t}
        for t in maturities
    ]
    builder = CurveBuilder(sample_data)
    bootstrapped = builder.bootstrapping()
    forward = builder.forward_curves()
    swaps = builder.swap_curves()
    return {
        "bootstrapped": bootstrapped,
        "forward_rates": forward,
        "swap_rates": swaps,
    }


@app.post("/curves/custom")
async def build_custom_curve(request: CurveRequest):
    """Build curves from caller-supplied market data."""
    if not request.market_data:
        raise HTTPException(status_code=400, detail="market_data must not be empty")
    builder = CurveBuilder(request.market_data)
    return {
        "bootstrapped": builder.bootstrapping(),
        "forward_rates": builder.forward_curves(),
        "swap_rates": builder.swap_curves(),
    }


@app.get("/spreads")
async def get_spreads():
    """Return the spread between ICE and NYMEX prices."""
    aggregator.fetch_data()
    data = aggregator.normalize_data()
    ice_prices = [d["value"] for d in data if d.get("source") == "ICE"]
    nymex_prices = [d["value"] for d in data if d.get("source") == "NYMEX"]

    if not ice_prices or not nymex_prices:
        return {"spreads": [], "message": "Insufficient data for spread calculation"}

    import numpy as np

    spread = float(np.mean(ice_prices) - np.mean(nymex_prices))
    return {"spreads": [{"ice_vs_nymex": spread}]}


@app.post("/messages")
async def send_message(request: MessageRequest):
    """Send a free-form notification via Telegram or SMS."""
    if request.channel == "telegram":
        success = await telegram.send_message(request.text)
    elif request.channel == "sms":
        if not request.to_number:
            raise HTTPException(status_code=400, detail="to_number is required for SMS")
        success = twilio.send_sms(request.to_number, request.text)
    else:
        raise HTTPException(status_code=400, detail=f"Unknown channel: {request.channel!r}")

    if not success:
        raise HTTPException(status_code=502, detail="Notification delivery failed")
    return {"message": "Message sent", "channel": request.channel}


@app.post("/alerts/price")
async def send_price_alert(request: AlertRequest):
    """Send a price-threshold alert via Telegram or SMS."""
    if request.channel == "telegram":
        success = await telegram.send_price_alert(
            request.contract, request.price, request.threshold, request.direction
        )
    elif request.channel == "sms":
        if not request.to_number:
            raise HTTPException(status_code=400, detail="to_number is required for SMS")
        success = twilio.send_price_alert(
            request.to_number, request.contract, request.price, request.threshold, request.direction
        )
    else:
        raise HTTPException(status_code=400, detail=f"Unknown channel: {request.channel!r}")

    if not success:
        raise HTTPException(status_code=502, detail="Alert delivery failed")
    return {"alert": "sent", "contract": request.contract, "channel": request.channel}
