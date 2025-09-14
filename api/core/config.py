# app/core/config.py
from typing import Annotated
from pydantic import Field
from pydantic import AnyUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

# Optional: Wenn du die URL streng typisieren willst (z. B. nur postgres/sqlite),
# könntest du stattdessen:
# from pydantic import UrlConstraints
# from typing import Annotated
# DatabaseUrl = Annotated[str, UrlConstraints(allowed_schemes=["postgresql+asyncpg", "sqlite+aiosqlite"])]

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # DATABASE_URL kann als str oder AnyUrl deklariert werden.
    # Bei AnyUrl meckert Pydantic nicht über "+asyncpg".
    DATABASE_URL: AnyUrl

    JWT_SECRET: str
    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_MINUTES: int = 15
    REFRESH_TOKEN_DAYS: int = 30

    KEY_HASH_SECRET: str

    FREE_MONTHLY_QUOTA: int = 10_000
    RATE_LIMIT_PER_MINUTE: int = 60

    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: str = "lax"
    COOKIE_DOMAIN: str | None = None

    STRIPE_SECRET_KEY: str
    STRIPE_WEBHOOK_SECRET: str
    STRIPE_PRICE_BASIC: str
    BASE_URL: str

    SENTRY_DSN: str
    SENTRY_TRACES_SAMPLE_RATE: float
    SENTRY_PROFILES_SAMPLE_RATE: float
    SENTRY_ENV: str = "production"

    SLACK_WEBHOOK_URL: str

    ALLOW_ORIGIN: str

settings = Settings()
