from repositories.base_repo import BaseRepository
from db.database import Database


class FeedbackRepository(BaseRepository):
    table = "feedback"

    def list_with_tour(self) -> list[dict]:
        conn = Database.connect()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT f.*, t.title AS tour_title
                FROM feedback f
                LEFT JOIN tours t ON t.id = f.tour_id
                ORDER BY f.id DESC
            """)
            return [dict(r) for r in cur.fetchall()]

    def avg_rating(self) -> float:
        conn = Database.connect()
        with conn.cursor() as cur:
            cur.execute("SELECT COALESCE(AVG(rating), 0) AS avg FROM feedback")
            return float(cur.fetchone()["avg"])