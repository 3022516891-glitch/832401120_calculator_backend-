import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator


DATA_DIRECTORY = Path(__file__).resolve().parent.parent / "data"
DATABASE_PATH = DATA_DIRECTORY / "calculator.db"


def database_url() -> str:
    url = os.environ.get("DATABASE_URL", "").strip()
    if url and not url.startswith(("postgresql://", "postgres://")):
        raise ValueError("DATABASE_URL 必须是 PostgreSQL 连接地址")
    if os.environ.get("VERCEL") and not url:
        raise RuntimeError("Vercel 部署必须设置 DATABASE_URL，不能使用本地 SQLite")
    return url


def execute_query(connection: Any, query: str, parameters=()):
    # 这里只转换程序内固定 SQL 的占位符；用户输入始终通过参数传递。
    if not isinstance(connection, sqlite3.Connection):
        query = query.replace("?", "%s")
    return connection.execute(query, parameters)


@contextmanager
def get_connection() -> Iterator[Any]:
    url = database_url()
    if url:
        import psycopg
        from psycopg.rows import dict_row

        connection = psycopg.connect(
            url, row_factory=dict_row, connect_timeout=10, prepare_threshold=None,
        )
    else:
        connection = sqlite3.connect(DATABASE_PATH)
        connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def initialize_database() -> None:
    if database_url():
        with get_connection() as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS calculation_history (
                    id BIGSERIAL PRIMARY KEY,
                    expression TEXT NOT NULL,
                    result DOUBLE PRECISION NOT NULL,
                    is_favorite INTEGER NOT NULL DEFAULT 0,
                    created_at TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC'),
                    angle_mode TEXT NOT NULL DEFAULT 'DEG',
                    note TEXT NOT NULL DEFAULT '',
                    tag TEXT NOT NULL DEFAULT ''
                )
            """)
            connection.execute(
                "ALTER TABLE calculation_history ADD COLUMN IF NOT EXISTS note TEXT NOT NULL DEFAULT ''"
            )
            connection.execute(
                "ALTER TABLE calculation_history ADD COLUMN IF NOT EXISTS tag TEXT NOT NULL DEFAULT ''"
            )
        return
    DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS calculation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                expression TEXT NOT NULL,
                result REAL NOT NULL,
                is_favorite INTEGER NOT NULL DEFAULT 0,
                note TEXT NOT NULL DEFAULT '',
                tag TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(calculation_history)")
        }
        if "is_favorite" not in columns:
            connection.execute(
                "ALTER TABLE calculation_history "
                "ADD COLUMN is_favorite INTEGER NOT NULL DEFAULT 0"
            )
        if "note" not in columns:
            connection.execute(
                "ALTER TABLE calculation_history ADD COLUMN note TEXT NOT NULL DEFAULT ''"
            )
        if "tag" not in columns:
            connection.execute(
                "ALTER TABLE calculation_history ADD COLUMN tag TEXT NOT NULL DEFAULT ''"
            )
        if "angle_mode" not in columns:
            connection.execute(
                "ALTER TABLE calculation_history ADD COLUMN angle_mode TEXT NOT NULL DEFAULT 'DEG'"
            )


if __name__ == "__main__":
    initialize_database()
    print("数据库初始化完成")
