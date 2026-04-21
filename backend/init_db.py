"""
数据库初始化脚本
创建所有数据表
"""

from app.database import engine, Base
from app.models import User, Property, SearchHistory, Report


def init_database():
    """创建所有表"""
    print("正在创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成！")

    # 显示创建的表
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"已创建的表: {tables}")


if __name__ == "__main__":
    init_database()
