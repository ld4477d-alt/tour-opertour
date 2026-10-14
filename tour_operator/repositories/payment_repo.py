from repositories.base_repo import BaseRepository
from db.database import Database


class PaymentRepository(BaseRepository):
    table = "payments"

    def list_with_contract(self) -> list[dict]:
        conn = Database.connect()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    p.*,
                    c.id AS contract_number,
                    cl.full_name AS client_name,
                    t.title AS tour_title
                FROM payments p
                JOIN contracts c ON c.id = p.contract_id
                JOIN clients cl  ON cl.id = c.client_id
                JOIN tours   t   ON t.id  = c.tour_id
                ORDER BY p.id DESC
            """)
            return [dict(r) for r in cur.fetchall()]

    def total_paid(self) -> float:
        conn = Database.connect()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT COALESCE(SUM(amount), 0) AS s "
                "FROM payments WHERE status = 'paid'"
            )
            return float(cur.fetchone()["s"])