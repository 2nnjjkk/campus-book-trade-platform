"""
应用配置模块
从 .env 文件加载敏感配置，并提供默认值。
"""

import os
from dotenv import load_dotenv

# 加载项目根目录的 .env 文件
load_dotenv()


class Config:
    """Flask 应用配置"""

    # Flask 密钥，用于 session 签名 —— 必须保密
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-change-me")

    # SQLite 数据库文件路径
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "book_trade.db")

    # 书籍图片上传目录
    UPLOAD_FOLDER: str = os.getenv("UPLOAD_FOLDER", "static/uploads")

    # 允许上传的图片类型
    ALLOWED_EXTENSIONS: set[str] = {"png", "jpg", "jpeg", "gif", "webp"}

    # 每页显示书籍数量
    BOOKS_PER_PAGE: int = 12
