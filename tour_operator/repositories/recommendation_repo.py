from repositories.base_repo import BaseRepository
from db.database import Database


class RecommendationRepository(BaseRepository):
    table = "recommendations"

    def list_with_author(self) -> list[dict]:
        conn = Database.connect()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT r.*, u.full_name AS author_name
                FROM recommendations r
                LEFT JOIN users u ON u.id = r.author_id
                ORDER BY r.id DESC
            """)
            return [dict(r) for r in cur.fetchall()]