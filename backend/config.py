import os
from dataclasses import dataclass, field


@dataclass
class Config:
    # ICE API
    ice_api_url: str = field(default_factory=lambda: os.getenv("ICE_API_URL", "https://api.ice.com"))
    ice_api_key: str = field(default_factory=lambda: os.getenv("ICE_API_KEY", ""))

    # Database
    db_host: str = field(default_factory=lambda: os.getenv("DB_HOST", "localhost"))
    db_port: int = field(default_factory=lambda: int(os.getenv("DB_PORT", "5432")))
    db_name: str = field(default_factory=lambda: os.getenv("DB_NAME", "gasoline_broker"))
    db_user: str = field(default_factory=lambda: os.getenv("DB_USER", "postgres"))
    db_password: str = field(default_factory=lambda: os.getenv("DB_PASSWORD", ""))

    # Telegram
    telegram_api_token: str = field(default_factory=lambda: os.getenv("TELEGRAM_API_TOKEN", ""))
    telegram_chat_id: str = field(default_factory=lambda: os.getenv("TELEGRAM_CHAT_ID", ""))

    # Twilio
    twilio_account_sid: str = field(default_factory=lambda: os.getenv("TWILIO_ACCOUNT_SID", ""))
    twilio_auth_token: str = field(default_factory=lambda: os.getenv("TWILIO_AUTH_TOKEN", ""))
    twilio_phone_number: str = field(default_factory=lambda: os.getenv("TWILIO_PHONE_NUMBER", ""))

    # Curve Building
    curve_low: float = field(default_factory=lambda: float(os.getenv("CURVE_LOW", "0.0")))
    curve_high: float = field(default_factory=lambda: float(os.getenv("CURVE_HIGH", "200.0")))

    @property
    def db_dsn(self) -> str:
        return (
            f"postgresql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


config = Config()
