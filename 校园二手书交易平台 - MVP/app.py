"""
校园二手书交易平台 - MVP
Flask 主应用，包含所有路由和 API 端点。
启动方式：python app.py
"""

import bcrypt
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    jsonify,
)

from config import Config
from models import init_db, User, Book
from utils.helpers import login_required, save_upload

# ---------------------------------------------------------------------------
# 应用初始化
# ---------------------------------------------------------------------------

app = Flask(__name__)
app.config.from_object(Config)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 上传限制 5 MB

# 首次启动时自动建表
init_db()


# ---------------------------------------------------------------------------
# 页面路由
# ---------------------------------------------------------------------------


@app.route("/")
def index() -> str:
    """首页：展示在售书籍列表，支持关键字搜索和分页。"""
    keyword = request.args.get("keyword", "").strip()
    page = request.args.get("page", 1, type=int)

    books, total = Book.find_all(keyword=keyword, page=page, per_page=Config.BOOKS_PER_PAGE)
    total_pages = max(1, (total + Config.BOOKS_PER_PAGE - 1) // Config.BOOKS_PER_PAGE)

    return render_template(
        "index.html",
        books=books,
        keyword=keyword,
        page=page,
        total_pages=total_pages,
        total=total,
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    """登录页面"""
    if request.method == "GET":
        return render_template("login.html")

    student_id = request.form.get("student_id", "").strip()
    password = request.form.get("password", "").strip()

    if not student_id or not password:
        flash("学号和密码不能为空。", "danger")
        return render_template("login.html")

    user = User.find_by_student_id(student_id)
    if user is None:
        flash("学号或密码错误。", "danger")
        return render_template("login.html")

    if not bcrypt.checkpw(password.encode("utf-8"), user["password_hash"].encode("utf-8")):
        flash("学号或密码错误。", "danger")
        return render_template("login.html")

    session["user_id"] = user["id"]
    session["nickname"] = user["nickname"]
    session["student_id"] = user["student_id"]

    flash(f"欢迎回来，{user['nickname']}！", "success")
    return redirect(url_for("index"))


@app.route("/register", methods=["GET", "POST"])
def register():
    """注册页面"""
    if request.method == "GET":
        return render_template("register.html")

    student_id = request.form.get("student_id", "").strip()
    nickname = request.form.get("nickname", "").strip()
    password = request.form.get("password", "").strip()
    confirm_password = request.form.get("confirm_password", "").strip()

    # 基本校验
    errors = []
    if not student_id:
        errors.append("学号不能为空。")
    if not nickname:
        errors.append("昵称不能为空。")
    if not password:
        errors.append("密码不能为空。")
    if len(password) < 6:
        errors.append("密码长度不能少于 6 位。")
    if password != confirm_password:
        errors.append("两次输入的密码不一致。")

    # 检查学号是否已注册
    if User.find_by_student_id(student_id):
        errors.append("该学号已被注册。")

    if errors:
        for e in errors:
            flash(e, "danger")
        return render_template("register.html")

    # bcrypt 哈希密码
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    user_id = User.create(student_id, password_hash, nickname)

    # 注册后自动登录
    session["user_id"] = user_id
    session["nickname"] = nickname
    session["student_id"] = student_id

    flash("注册成功，欢迎加入！", "success")
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    """退出登录"""
    session.clear()
    flash("已退出登录。", "info")
    return redirect(url_for("index"))


@app.route("/publish", methods=["GET", "POST"])
@login_required
def publish():
    """发布新书籍页面"""
    if request.method == "GET":
        return render_template("publish.html")

    title = request.form.get("title", "").strip()
    price_str = request.form.get("price", "").strip()
    original_price_str = request.form.get("original_price", "").strip()
    description = request.form.get("description", "").strip()
    contact = request.form.get("contact", "").strip()
    image_file = request.files.get("image")

    # 校验必填字段
    errors = []
    if not title:
        errors.append("书名不能为空。")
    if not price_str:
        errors.append("售价不能为空。")
    else:
        try:
            price = float(price_str)
            if price <= 0:
                errors.append("售价必须大于 0。")
        except ValueError:
            errors.append("售价格式不正确。")

    if not contact:
        errors.append("联系方式不能为空。")

    original_price = None
    if original_price_str:
        try:
            original_price = float(original_price_str)
        except ValueError:
            errors.append("原价格式不正确。")

    if errors:
        for e in errors:
            flash(e, "danger")
        return render_template("publish.html")

    # 处理图片上传
    image_url = save_upload(image_file) if image_file and image_file.filename else None

    Book.create(
        user_id=session["user_id"],
        title=title,
        price=price,
        contact=contact,
        original_price=original_price,
        description=description or None,
        image_url=image_url,
    )

    flash("发布成功！", "success")
    return redirect(url_for("index"))


@app.route("/book/<int:book_id>")
def detail(book_id: int) -> str:
    """书籍详情页"""
    book = Book.find_by_id(book_id)
    if book is None:
        flash("该书籍不存在或已下架。", "warning")
        return redirect(url_for("index"))
    return render_template("detail.html", book=book)


@app.route("/book/<int:book_id>/toggle", methods=["POST"])
@login_required
def toggle_status(book_id: int):
    """切换书籍上下架状态（仅发布者本人）"""
    book = Book.find_by_id(book_id)
    if book is None:
        flash("该书籍不存在。", "warning")
        return redirect(url_for("index"))

    if book["user_id"] != session["user_id"]:
        flash("你没有权限操作该书籍。", "danger")
        return redirect(url_for("detail", book_id=book_id))

    new_status = 1 if book["status"] == 0 else 0
    Book.update_status(book_id, session["user_id"], new_status)
    action = "上架" if new_status == 1 else "下架"
    flash(f"书籍已{action}。", "success")
    return redirect(url_for("detail", book_id=book_id))


# ---------------------------------------------------------------------------
# API 路由（JSON 响应，供前端 Ajax 或外部调用）
# ---------------------------------------------------------------------------


@app.route("/api/register", methods=["POST"])
def api_register():
    """用户注册 API"""
    data = request.get_json(silent=True) or {}
    student_id = data.get("student_id", "").strip()
    nickname = data.get("nickname", "").strip()
    password = data.get("password", "").strip()

    if not student_id or not nickname or not password:
        return jsonify({"error": "缺少必填字段"}), 400
    if len(password) < 6:
        return jsonify({"error": "密码长度不能少于 6 位"}), 400
    if User.find_by_student_id(student_id):
        return jsonify({"error": "该学号已被注册"}), 409

    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    user_id = User.create(student_id, password_hash, nickname)

    return jsonify({"id": user_id, "student_id": student_id, "nickname": nickname}), 201


@app.route("/api/login", methods=["POST"])
def api_login():
    """用户登录 API，返回用户基本信息。"""
    data = request.get_json(silent=True) or {}
    student_id = data.get("student_id", "").strip()
    password = data.get("password", "").strip()

    if not student_id or not password:
        return jsonify({"error": "学号和密码不能为空"}), 400

    user = User.find_by_student_id(student_id)
    if user is None:
        return jsonify({"error": "学号或密码错误"}), 401

    if not bcrypt.checkpw(password.encode("utf-8"), user["password_hash"].encode("utf-8")):
        return jsonify({"error": "学号或密码错误"}), 401

    session["user_id"] = user["id"]
    session["nickname"] = user["nickname"]
    session["student_id"] = user["student_id"]

    return jsonify({
        "id": user["id"],
        "student_id": user["student_id"],
        "nickname": user["nickname"],
    })


@app.route("/api/books", methods=["GET", "POST"])
def api_books():
    """
    GET  ——获取在售书籍列表，支持 ?keyword= 模糊搜索和 ?page= 分页。
    POST ——发布新书（需登录）。
    """
    if request.method == "GET":
        keyword = request.args.get("keyword", "").strip()
        page = request.args.get("page", 1, type=int)
        books, total = Book.find_all(keyword=keyword, page=page, per_page=Config.BOOKS_PER_PAGE)
        return jsonify({
            "books": books,
            "total": total,
            "page": page,
            "per_page": Config.BOOKS_PER_PAGE,
        })

    # POST ——发布
    if "user_id" not in session:
        return jsonify({"error": "请先登录"}), 401

    data = request.get_json(silent=True) or {}
    title = data.get("title", "").strip()
    price = data.get("price")
    contact = data.get("contact", "").strip()

    if not title or price is None or not contact:
        return jsonify({"error": "书名、售价、联系方式为必填项"}), 400

    try:
        price = float(price)
    except (TypeError, ValueError):
        return jsonify({"error": "售价格式不正确"}), 400

    original_price = data.get("original_price")
    if original_price is not None:
        try:
            original_price = float(original_price)
        except (TypeError, ValueError):
            return jsonify({"error": "原价格式不正确"}), 400

    book_id = Book.create(
        user_id=session["user_id"],
        title=title,
        price=price,
        contact=contact,
        original_price=original_price,
        description=data.get("description"),
        image_url=data.get("image_url"),
    )

    return jsonify({"id": book_id, "title": title}), 201


@app.route("/api/books/<int:book_id>")
def api_book_detail(book_id: int):
    """获取指定书籍详情 API"""
    book = Book.find_by_id(book_id)
    if book is None:
        return jsonify({"error": "书籍不存在或已下架"}), 404
    return jsonify(book)


# ---------------------------------------------------------------------------
# 启动入口
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
