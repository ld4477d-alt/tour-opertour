from repositories.base_repo import BaseRepository
from db.database import Database


class AuditRepository(BaseRepository):
    table = "audit_log"

    def log(self, user_id: int | None, action: str,
            entity: str | None = None, entity_id: int | None = None,
            details: str | None = None) -> None:
        conn = Database.connect()
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO audit_log
                       (user_id, action, entity, entity_id, details)
                   VALUES (%s, %s, %s, %s, %s)""",
                (user_id, action, entity, entity_id, details),
            )
        conn.commit()

    def list_with_user(self) -> list[dict]:
        conn = Database.connect()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT a.*, u.full_name AS user_name
                FROM audit_log a
                LEFT JOIN users u ON u.id = a.user_id
                ORDER BY a.id DESC
                LIMIT 500
            """)
            return [dict(r) for r in cur.fetchall()]