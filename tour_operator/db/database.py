import psycopg2
from psycopg2.extras import RealDictCursor
from pathlib import Path

from config import DB_CONFIG

SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"


class Database:
    """Единая точка подключения к PostgreSQL."""
    _conn = None

    @classmethod
    def connect(cls):
        if cls._conn is None or cls._conn.closed:
            cls._conn = psycopg2.connect(
                **DB_CONFIG,
                cursor_factory=RealDictCursor,
            )
            cls._conn.autocommit = False
        return cls._conn

    @classmethod
    def init_schema(cls) -> None:
        """Применяет schema.sql (идемпотентно)."""
        conn = cls.connect()
        with conn.cursor() as cur:
            cur.execute(SCHEMA_PATH.read_text(encoding="utf-8"))
        conn.commit()

    @classmethod
    def close(cls) -> None:
        if cls._conn is not None and not cls._conn.closed:
            cls._conn.close()
            cls._conn = None