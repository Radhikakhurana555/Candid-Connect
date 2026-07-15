from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterable

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "recruitment.db"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


@contextmanager
def connection_scope():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    with connection_scope() as conn:
        conn.executescript(schema)


def execute(query: str, params: Iterable[Any] = ()) -> None:
    with connection_scope() as conn:
        conn.execute(query, tuple(params))


def executemany(query: str, rows: Iterable[Iterable[Any]]) -> None:
    with connection_scope() as conn:
        conn.executemany(query, rows)


def fetch_all(query: str, params: Iterable[Any] = ()) -> list[dict[str, Any]]:
    with connection_scope() as conn:
        result = conn.execute(query, tuple(params)).fetchall()
        return [dict(row) for row in result]


def fetch_one(query: str, params: Iterable[Any] = ()) -> dict[str, Any] | None:
    with connection_scope() as conn:
        row = conn.execute(query, tuple(params)).fetchone()
        return dict(row) if row else None
