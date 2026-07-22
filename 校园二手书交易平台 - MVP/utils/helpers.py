"""
工具函数模块
包含登录验证装饰器、文件上传校验等辅助功能。
"""

import os
import uuid
from functools import wraps
from flask import session, redirect, url_for, flash
from werkzeug.datastructures import FileStorage
from config import Config


def login_required(f):
    """
    装饰器：要求用户已登录才能访问受保护的路由。
    未登录时重定向到登录页并提示。
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("请先登录后再操作。", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


def allowed_file(filename: str) -> bool:
    """检查文件扩展名是否在允许列表中。"""
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in Config.ALLOWED_EXTENSIONS


def save_upload(file: FileStorage) -> str | None:
    """
    安全保存上传的图片文件，返回相对于 static 文件夹的路径。
    - 校验扩展名
    - 使用 UUID 重命名避免冲突和路径遍历攻击
    - 自动创建上传目录（若不存在）
    """
    if file is None or file.filename == "":
        return None

    if not allowed_file(file.filename):
        return None

    # 确保上传目录存在
    upload_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        Config.UPLOAD_FOLDER,
    )
    os.makedirs(upload_dir, exist_ok=True)

    # 用 UUID 生成唯一文件名，保留原始扩展名
    ext = file.filename.rsplit(".", 1)[1].lower()
    new_filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(upload_dir, new_filename)
    file.save(filepath)

    # 返回相对于 static 的路径（供模板使用）
    return f"uploads/{new_filename}"
