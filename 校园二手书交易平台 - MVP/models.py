"""
数据库模型模块
封装所有 SQLite 操作，提供 Users 和 Books 两个模型类。
"""

import sqlite3
from datetime import datetime
from config import Config


def get_db() -> sqlite3.Connection:
    """获取数据库连接，并启用行工厂以便通过字段名访问结果。"""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db() -> None:
    """创建应用所需的全部数据表（仅在首次运行时执行）。"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER  PRIMARY KEY AUTOINCREMENT,
            student_id    TEXT     NOT NULL UNIQUE,
            password_hash TEXT     NOT NULL,
            nickname      TEXT     NOT NULL,
            created_at    DATETIME NOT NULL DEFAULT (datetime('now', 'localtime'))
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id             INTEGER  PRIMARY KEY AUTOINCREMENT,
            user_id        INTEGER  NOT NULL,
            title          TEXT     NOT NULL,
            price          REAL     NOT NULL,
            original_price REAL,
            description    TEXT,
            contact        TEXT     NOT NULL,
            image_url      TEXT,
            status         INTEGER  NOT NULL DEFAULT 1,
            created_at     DATETIME NOT NULL DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# 用户模型
# ---------------------------------------------------------------------------

class User:
    """用户相关数据库操作"""

    @staticmethod
    def create(student_id: str, password_hash: str, nickname: str) -> int:
        """创建新用户，返回新用户的 id。"""
        conn = get_db()
        try:
            cursor = conn.execute(
                "INSERT INTO users (student_id, password_hash, nickname) VALUES (?, ?, ?)",
                (student_id, password_hash, nickname),
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    @staticmethod
    def find_by_student_id(student_id: str) -> dict | None:
        """通过学号查找用户，返回字典或 None。"""
        conn = get_db()
        try:
            row = conn.execute(
                "SELECT * FROM users WHERE student_id = ?", (student_id,)
            ).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    @staticmethod
    def find_by_id(user_id: int) -> dict | None:
        """通过主键查找用户。"""
        conn = get_db()
        try:
            row = conn.execute(
                "SELECT * FROM users WHERE id = ?", (user_id,)
            ).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()


# ---------------------------------------------------------------------------
# 书籍模型
# ---------------------------------------------------------------------------

class Book:
    """书籍相关数据库操作"""

    @staticmethod
    def create(
        user_id: int,
        title: str,
        price: float,
        contact: str,
        original_price: float | None = None,
        description: str | None = None,
        image_url: str | None = None,
    ) -> int:
        """发布新书，返回新书籍的 id。"""
        conn = get_db()
        try:
            cursor = conn.execute(
                """INSERT INTO books
                   (user_id, title, price, original_price, description, contact, image_url)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (user_id, title, price, original_price, description, contact, image_url),
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    @staticmethod
    def find_all(keyword: str = "", page: int = 1, per_page: int = 12) -> tuple[list[dict], int]:
        """
        分页查询在售书籍，支持书名模糊搜索。
        返回 (书籍列表, 总条数)。
        """
        conn = get_db()
        try:
            base_query = """
                SELECT b.*, u.nickname AS seller_nickname, u.student_id AS seller_student_id
                FROM books b
                JOIN users u ON b.user_id = u.id
                WHERE b.status = 1
            """
            params: tuple = ()

            if keyword.strip():
                base_query += " AND b.title LIKE ?"
                params = (f"%{keyword.strip()}%",)

            # 总数
            count_query = base_query.replace(
                "SELECT b.*, u.nickname AS seller_nickname, u.student_id AS seller_student_id",
                "SELECT COUNT(*)",
            )
            total = conn.execute(count_query, params).fetchone()[0]

            # 分页 + 按发布时间倒序
            offset = (page - 1) * per_page
            data_query = base_query + " ORDER BY b.created_at DESC LIMIT ? OFFSET ?"
            rows = conn.execute(data_query, (*params, per_page, offset)).fetchall()

            return [dict(r) for r in rows], total
        finally:
            conn.close()

    @staticmethod
    def find_by_id(book_id: int) -> dict | None:
        """查询单本书详情（含卖家昵称）。"""
        conn = get_db()
        try:
            row = conn.execute(
                """SELECT b.*, u.nickname AS seller_nickname, u.student_id AS seller_student_id
                   FROM books b
                   JOIN users u ON b.user_id = u.id
                   WHERE b.id = ?""",
                (book_id,),
            ).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    @staticmethod
    def find_by_user(user_id: int, page: int = 1, per_page: int = 12) -> tuple[list[dict], int]:
        """查询某用户发布的所有书籍。"""
        conn = get_db()
        try:
            count = conn.execute(
                "SELECT COUNT(*) FROM books WHERE user_id = ?", (user_id,)
            ).fetchone()[0]
            offset = (page - 1) * per_page
            rows = conn.execute(
                """SELECT b.*, u.nickname AS seller_nickname
                   FROM books b
                   JOIN users u ON b.user_id = u.id
                   WHERE b.user_id = ?
                   ORDER BY b.created_at DESC LIMIT ? OFFSET ?""",
                (user_id, per_page, offset),
            ).fetchall()
            return [dict(r) for r in rows], count
        finally:
            conn.close()

    @staticmethod
    def update_status(book_id: int, user_id: int, status: int) -> bool:
        """下架/上架书籍（仅限发布者本人操作）。返回是否成功。"""
        conn = get_db()
        try:
            cursor = conn.execute(
                "UPDATE books SET status = ? WHERE id = ? AND user_id = ?",
                (status, book_id, user_id),
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
