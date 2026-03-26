import asyncpg
import logging
from typing import Optional
from backend.config import config

logger = logging.getLogger(__name__)

_pool: Optional[asyncpg.Pool] = None

CREATE_PRICES_TABLE = """
CREATE TABLE IF NOT EXISTS prices (
    id          SERIAL PRIMARY KEY,
    source      VARCHAR(50)   NOT NULL,
    contract    VARCHAR(100)  NOT NULL,
    price       NUMERIC(18,6) NOT NULL,
    currency    VARCHAR(10)   NOT NULL DEFAULT 'USD',
    recorded_at TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);
"""

CREATE_TRADES_TABLE = """
CREATE TABLE IF NOT EXISTS trades (
    id          SERIAL PRIMARY KEY,
    contract    VARCHAR(100)  NOT NULL,
    side        VARCHAR(4)    NOT NULL CHECK (side IN ('BUY', 'SELL')),
    quantity    NUMERIC(18,6) NOT NULL,
    price       NUMERIC(18,6) NOT NULL,
    status      VARCHAR(20)   NOT NULL DEFAULT 'OPEN',
    created_at  TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);
"""

CREATE_ALERTS_TABLE = """
CREATE TABLE IF NOT EXISTS alerts (
    id          SERIAL PRIMARY KEY,
    contract    VARCHAR(100)  NOT NULL,
    threshold   NUMERIC(18,6) NOT NULL,
    direction   VARCHAR(5)    NOT NULL CHECK (direction IN ('ABOVE', 'BELOW')),
    channel     VARCHAR(20)   NOT NULL DEFAULT 'telegram',
    active      BOOLEAN       NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);
"""


async def get_pool() -> asyncpg.Pool:
    """Return the shared connection pool, creating it on first call."""
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            dsn=config.db_dsn,
            min_size=2,
            max_size=10,
        )
        logger.info("Database connection pool created.")
    return _pool


async def init_db() -> None:
    """Create tables if they do not exist."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(CREATE_PRICES_TABLE)
        await conn.execute(CREATE_TRADES_TABLE)
        await conn.execute(CREATE_ALERTS_TABLE)
    logger.info("Database schema initialised.")


async def close_pool() -> None:
    """Close the connection pool gracefully."""
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None
        logger.info("Database connection pool closed.")
