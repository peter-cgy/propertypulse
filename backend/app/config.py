from pydantic_settings import BaseSettings
from typing import Optional
from dotenv import load_dotenv
import os

# 加载 .env 文件
load_dotenv()


class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "PropertyPulse"
    DEBUG: bool = True

    # 数据库配置
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/propertypulse"

    # JWT配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天

    # API Keys
    RENTCAST_API_KEY: str = ""
    GREATSCHOOLS_API_KEY: str = ""

    # LemonSqueezy配置
    LEMONSQUEEZY_API_KEY: str = ""
    LEMONSQUEEZY_STORE_ID: str = ""
    LEMONSQUEEZY_WEBHOOK_SECRET: str = ""

    # 产品ID（创建产品后填入）
    LEMONSQUEEZY_FREE_VARIANT_ID: str = ""
    LEMONSQUEEZY_STARTER_VARIANT_ID: str = ""
    LEMONSQUEEZY_PRO_VARIANT_ID: str = ""
    LEMONSQUEEZY_TEAM_VARIANT_ID: str = ""

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "https://propertypulse.vercel.app"]

    # Production URL (will be set in deployment)
    FRONTEND_URL: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
