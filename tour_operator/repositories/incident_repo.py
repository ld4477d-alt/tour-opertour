from repositories.base_repo import BaseRepository
from db.database import Database


class IncidentRepository(BaseRepository):
    table = "incidents"

    def list_with_tour(self) -> list[dict]:
        conn = Database.connect()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    i.*,
                    t.title AS tour_title,
                    a.full_name AS author_name,
                    s.full_name AS assignee_name
                FROM incidents i
                JOIN tours t ON t.id = i.tour_id
                LEFT JOIN users a ON a.id = i.author_id
                LEFT JOIN users s ON s.id = i.assignee_id
                ORDER BY i.id DESC
            """)
            return [dict(r) for r in cur.fetchall()]

    def resolve(self, pk: int, solution: str) -> None:
        conn = Database.connect()
        with conn.cursor() as cur:
            cur.execute(
                """UPDATE incidents
                   SET status = 'resolved',
                       solution = %s,
                       closed_at = NOW()
                   WHERE id = %s""",
                (solution, pk),
            )
        conn.commit()

    def assign(self, pk: int, user_id: int) -> None:
        conn = Database.connect()
        with conn.cursor() as cur:
            cur.execute(
                """UPDATE incidents
                   SET assignee_id = %s, status = 'in_work'
                   WHERE id = %s""",
                (user_id, pk),
            )
        conn.commit()