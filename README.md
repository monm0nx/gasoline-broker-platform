# Gasoline Broker Platform

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                      API Layer (FastAPI)                 │
│  GET /prices  GET /curves  GET /spreads  POST /messages  │
│               POST /curves/custom  POST /alerts/price    │
└───────────────┬─────────────────────────────────────────┘
                │
   ┌────────────┼────────────┬─────────────────┐
   ▼            ▼            ▼                 ▼
Market Data  Curve Builder  Notifications    Database
Aggregator   (CurveBuilder) (Telegram/SMS)  (asyncpg)
   │
   ▼
ICE WebSocket
Connector
```

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python, FastAPI, uvicorn |
| **Real-time data** | ICE WebSocket API (websocket-client) |
| **Curve building** | NumPy, SciPy (spline/polynomial interpolation, bootstrapping) |
| **Database** | PostgreSQL via asyncpg |
| **Time-series DB** | InfluxDB (Docker, ready to integrate) |
| **Cache** | Redis (Docker, ready to integrate) |
| **Notifications** | Telegram Bot API, Twilio SMS |
| **Testing** | pytest, pytest-asyncio |
| **Containers** | Docker Compose (PostgreSQL, InfluxDB, Redis) |

## Installation Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/monm0nx/gasoline-broker-platform.git
   cd gasoline-broker-platform
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and fill in your credentials
   ```

4. **Start backing services**
   ```bash
   docker-compose up -d
   ```

5. **Run the API server**
   ```bash
   uvicorn backend.api.routes:app --reload --port 3000
   ```

6. **Run tests**
   ```bash
   pytest
   ```

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/prices` | Latest normalised market prices (ICE, NYMEX, brokers) |
| GET | `/curves` | Bootstrapped, forward-rate, and swap-rate curves |
| GET | `/spreads` | ICE vs NYMEX price spread |
| POST | `/curves/custom` | Build curves from caller-supplied market data |
| POST | `/messages` | Send a free-form notification (Telegram or SMS) |
| POST | `/alerts/price` | Send a formatted price-threshold alert |

Interactive docs are served by FastAPI at `http://localhost:3000/docs`.

## ICE API Integration Guide

### Configuration

1. **Sign up for ICE API**: Visit [ICE API](https://iceapi.com) and sign up for an account to obtain your API key.

2. **Adding the API Key to your application**: Set `ICE_API_KEY` in your `.env` file.

### Authentication Flow Example

1. **Requesting a token**
   ```http
   POST https://api.ice.com/auth/token
   ```
   ```json
   { "api_key": "your_api_key_here" }
   ```
   Response: `{ "token": "your_jwt_token_here" }`

2. **Using the token**
   ```http
   GET https://api.ice.com/data
   Authorization: Bearer your_jwt_token_here
   ```

## Next Steps

The following features are the next priorities for making this platform production-ready:

### 🚀 High Priority

1. **Trade Execution Engine**
   - Implement buy/sell order placement and tracking (`backend/services/trading/`)
   - Build P&L calculation and position management
   - Add order history with full audit trail

2. **User Authentication & Authorisation**
   - JWT-based auth middleware for the FastAPI routes
   - Role-based access control (admin, trader, viewer)
   - Secure session management

3. **Database Integration**
   - Wire `backend/db/database.py` into the API startup lifecycle (`@app.on_event`)
   - Implement repository classes for prices, trades, and alerts
   - Add Alembic migrations for schema versioning

4. **Real-time Price Storage**
   - Persist incoming ICE WebSocket prices to PostgreSQL/InfluxDB
   - Connect `IceConnector.handle_message()` to the database layer
   - Expose historical time-series via a `/prices/history` endpoint

### 🛠 Medium Priority

5. **Frontend (React.js)**
   - Dashboard with live price chart (WebSocket push or polling)
   - Order entry and portfolio overview screens
   - Admin panel for alert configuration

6. **Redis Caching**
   - Cache latest prices to reduce database load
   - Use pub/sub for broadcasting real-time updates to the frontend

7. **InfluxDB Time-Series**
   - Store high-frequency tick data in InfluxDB
   - Build analytics queries for OHLCV aggregations

8. **Risk Management Module**
   - Value at Risk (VaR) and exposure-limit enforcement
   - Daily P&L reporting
   - Threshold-based alerts wired to the notification services

### 🔧 Operations

9. **CI/CD Pipeline** – GitHub Actions workflow for lint → test → build → deploy
10. **Monitoring** – Prometheus metrics + Grafana dashboard
11. **Kubernetes Manifests** – Helm chart for production deployment
12. **Backup & Disaster Recovery** – Automated PostgreSQL snapshots

