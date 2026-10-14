from typing import Any
from db.database import Database


class BaseRepository:
    """Базовый CRUD-репозиторий. Наследники задают table."""
    table: str = ""

    def all(self) -> list[dict[str, Any]]:
        conn = Database.connect()
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM {self.table} ORDER BY id")
            return [dict(r) for r in cur.fetchall()]

    def get(self, pk: int) -> dict[str, Any] | None:
        conn = Database.connect()
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM {self.table} WHERE id = %s", (pk,))
            row = cur.fetchone()
            return dict(row) if row else None

    def insert(self, data: dict[str, Any]) -> int:
        keys = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        conn = Database.connect()
        with conn.cursor() as cur:
            cur.execute(
                f"INSERT INTO {self.table} ({keys}) "
                f"VALUES ({placeholders}) RETURNING id",
                tuple(data.values()),
            )
            new_id = cur.fetchone()["id"]
        conn.commit()
        return new_id

    def update(self, pk: int, data: dict[str, Any]) -> None:
        assignments = ", ".join(f"{k} = %s" for k in data)
        conn = Database.connect()
        with conn.cursor() as cur:
            cur.execute(
                f"UPDATE {self.table} SET {assignments} WHERE id = %s",
                (*data.values(), pk),
            )
        conn.commit()

    def delete(self, pk: int) -> None:
        conn = Database.connect()
        with conn.cursor() as cur:
            cur.execute(f"DELETE FROM {self.table} WHERE id = %s", (pk,))
        conn.commit()

    def search(self, field: str, value: str) -> list[dict[str, Any]]:
        conn = Database.connect()
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {self.table} WHERE {field} ILIKE %s ORDER BY id",
                (f"%{value}%",),
            )
            return [dict(r) for r in cur.fetchall()]