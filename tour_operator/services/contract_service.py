"""Сервис работы с договорами (заявками)."""
from repositories.contract_repo import ContractRepository
from db.database import Database


class ContractService:
    def __init__(self):
        self.repo = ContractRepository()

    def list_all(self) -> list[dict]:
        """Возвращает все договоры вместе с ФИО клиента, названием тура и менеджером."""
        conn = Database.connect()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    c.id,
                    c.created_at,
                    c.status,
                    c.total,
                    cl.full_name  AS client_name,
                    cl.phone      AS client_phone,
                    t.title       AS tour_title,
                    t.date_start  AS tour_start,
                    t.date_end    AS tour_end,
                    u.full_name   AS manager_name
                FROM contracts c
                JOIN clients cl ON cl.id = c.client_id
                JOIN tours   t  ON t.id  = c.tour_id
                LEFT JOIN users u ON u.id = c.manager_id
                ORDER BY c.id DESC
            """)
            return [dict(r) for r in cur.fetchall()]

    def search(self,
               status: str | None = None,
               date_from: str | None = None,
               date_to: str | None = None) -> list[dict]:
        """Фильтрованный список договоров."""
        sql = """
            SELECT
                c.id, c.created_at, c.status, c.total,
                cl.full_name AS client_name,
                cl.phone     AS client_phone,
                t.title      AS tour_title,
                t.date_start AS tour_start,
                t.date_end   AS tour_end,
                u.full_name  AS manager_name
            FROM contracts c
            JOIN clients cl ON cl.id = c.client_id
            JOIN tours   t  ON t.id  = c.tour_id
            LEFT JOIN users u ON u.id = c.manager_id
            WHERE 1 = 1
        """
        params: list = []

        if status and status != "Все":
            sql += " AND c.status = %s"
            params.append(status)

        if date_from:
            sql += " AND c.created_at >= %s"
            params.append(date_from)

        if date_to:
            sql += " AND c.created_at <= %s"
            params.append(date_to)

        sql += " ORDER BY c.id DESC"

        conn = Database.connect()
        with conn.cursor() as cur:
            cur.execute(sql, tuple(params))
            return [dict(r) for r in cur.fetchall()]

    def get_details(self, contract_id: int) -> dict | None:
        conn = Database.connect()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    c.id, c.created_at, c.status, c.total,
                    cl.full_name AS client_name,
                    cl.phone     AS client_phone,
                    cl.email     AS client_email,
                    cl.passport  AS client_passport,
                    t.title      AS tour_title,
                    t.date_start AS tour_start,
                    t.date_end   AS tour_end,
                    t.price      AS tour_price,
                    u.full_name  AS manager_name
                FROM contracts c
                JOIN clients cl ON cl.id = c.client_id
                JOIN tours   t  ON t.id  = c.tour_id
                LEFT JOIN users u ON u.id = c.manager_id
                WHERE c.id = %s
            """, (contract_id,))
            row = cur.fetchone()
            return dict(row) if row else None

    def update_status(self, contract_id: int, new_status: str) -> None:
        conn = Database.connect()
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE contracts SET status = %s WHERE id = %s",
                (new_status, contract_id),
            )
        conn.commit()