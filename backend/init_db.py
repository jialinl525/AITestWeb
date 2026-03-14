"""
初始化数据库，创建表结构
"""
from database import engine, Base
import models  # noqa: F401 - needed so model classes register with Base.metadata

def init_db():
    """创建所有数据库表"""
    Base.metadata.create_all(bind=engine)
    print("数据库表创建成功！")

if __name__ == "__main__":
    init_db()
