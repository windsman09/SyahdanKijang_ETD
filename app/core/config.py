# app/core/config.py
import os
from pydantic import BaseModel
from dotenv import load_dotenv

# Muat .env dari root project saat startup
load_dotenv()

class Settings(BaseModel):
    # Aplikasi
    app_name: str = os.getenv("APP_NAME", "FastAPI Template")
    env: str = os.getenv("APP_ENV", "development")
    host: str = os.getenv("APP_HOST", "0.0.0.0")
    port: int = int(os.getenv("APP_PORT", "8000"))
    cors_origins: list[str] = [s.strip() for s in os.getenv("CORS_ORIGINS", "").split(",") if s.strip()]

    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")

    # Auth
    secret_key: str = os.getenv("SECRET_KEY", "change-this-in-production-please")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

    # Polling
    polling_interval: int = int(os.getenv("POLLING_INTERVAL", "5"))

    # ETD target (dibaca dari .env)
    etd_host: str = os.getenv("ETD_HOST", "10.21.240.5")
    etd_port: int = int(os.getenv("ETD_PORT", "5000"))
    etd_unit: int = int(os.getenv("ETD_UNIT", "1"))

settings = Settings()
