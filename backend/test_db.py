# -*- coding: utf-8 -*-
"""
测试数据库连接
"""

from sqlalchemy import create_engine, text
from app.config import settings


def test_connection():
    """测试数据库连接"""
    print(f"Database URL: {settings.DATABASE_URL}")

    try:
        if settings.DATABASE_URL.startswith("sqlite"):
            engine = create_engine(
                settings.DATABASE_URL,
                connect_args={"check_same_thread": False}
            )
        else:
            engine = create_engine(settings.DATABASE_URL)

        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
        print("[SUCCESS] Database connection successful!")
        return True
    except Exception as e:
        print(f"[FAILED] Database connection failed: {e}")
        return False


if __name__ == "__main__":
    test_connection()
