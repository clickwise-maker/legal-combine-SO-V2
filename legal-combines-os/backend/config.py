# FRAMEWORK PLACEHOLDER
# DO NOT DELETE
# IMPLEMENT IN FUTURE PHASE: Phase 3

import os
from typing import Optional

class Settings:
    """Application settings."""

    # App
    APP_NAME: str = "Legal Combines OS"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///legal_combines.db")

    # JWT
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Razorpay
    RAZORPAY_KEY_ID: str = os.getenv("RAZORPAY_KEY_ID", "")
    RAZORPAY_KEY_SECRET: str = os.getenv("RAZORPAY_KEY_SECRET", "")
    RAZORPAY_WEBHOOK_SECRET: str = os.getenv("RAZORPAY_WEBHOOK_SECRET", "")

    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]

    # Scraper
    SCRAPER_USER_AGENT: str = "LegalCombinesOS/1.0"
    SCRAPER_RATE_LIMIT: float = 2.0

    # Commission
    MARKETPLACE_COMMISSION_RATE: float = 0.12

settings = Settings()
