"""Окно бухгалтерии."""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel
)

from db.database import Database


class AccountantWindow(QMainWindow):
    TAX_RATE = 0.06

    def __init__(self, user):
        super().__init__()
        self.user = user

        self.setWindowTitle(f"Бухгалтерия — {user.full_name}")
        self.resize(1050, 620)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        menu_bar = QHBoxLayout()
        for name in ("Сводка", "Налоги", "Статистика",
                     "Сверка с поставщиками"):
            btn = QPushButton(name)
            btn.clicked.connect(lambda _, n=name: self._switch_section(n))
            menu_bar.addWidget(btn)
        root.addLayout(menu_bar)

        toolbar = QHBoxLayout()
        refresh_btn = QPushButton("Обновить")
        refresh_btn.clicked.connect(self._refresh)
        toolbar.addWidget(refresh_btn)
        root.addLayout(toolbar)

        self.table = QTableWidget(0, 2)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        root.addWidget(self.table)

        self.section_label = QLabel("Раздел: Сводка")
        root.addWidget(self.section_label)

        self.current_section = "Сводка"
        self._switch_section("Сводка")

    def _switch_section(self, name: str):
        self.current_section = name
        self.section_label.setText(f"Раздел: {name}")
        self._refresh()

    def _refresh(self):
        s = self.current_section
        if s == "Сводка":       self._load_summary()
        elif s == "Налоги":     self._load_taxes()
        elif s == "Статистика": self._load_statistics()
        elif s == "Сверка с поставщиками":
            self._load_reconciliation()

    def _load_summary(self):
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Показатель", "Значение"])
        self.table.setRowCount(0)
        conn = Database.connect()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*) AS c,
                       COALESCE(SUM(total), 0) AS revenue
                FROM contracts
                WHERE status IN ('Оформлен','Оплачен')
            """)
            r = cur.fetchone()
        for label, value in [
            ("Всего заявок", str(r["c"])),
            ("Выручка",      f"{float(r['revenue']):,.2f} ₽"),
        ]:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(label))
            self.table.setItem(row, 1, QTableWidgetItem(value))

    def _load_taxes(self):
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Показатель", "Значение"])
        self.table.setRowCount(0)
        conn = Database.connect()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT COALESCE(SUM(total), 0) AS revenue
                FROM contracts
                WHERE status IN ('Оформлен','Оплачен')
            """)
            revenue = float(cur.fetchone()["revenue"])
        tax = revenue * self.TAX_RATE
        net = revenue - tax
        for label, value in [
            ("Выручка", f"{revenue:,.2f} ₽"),
            (f"Налог (УСН {int(self.TAX_RATE*100)}%)",
             f"{tax:,.2f} ₽"),
            ("Чистая выручка", f"{net:,.2f} ₽"),
        ]:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(label))
            self.table.setItem(row, 1, QTableWidgetItem(value))

    def _load_statistics(self):
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(
            ["Месяц", "Заявок", "Сумма"]
        )
        self.table.setRowCount(0)
        conn = Database.connect()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT TO_CHAR(created_at, 'YYYY-MM') AS month,
                       COUNT(*) AS cnt,
                       COALESCE(SUM(total), 0) AS total
                FROM contracts
                GROUP BY month
                ORDER BY month DESC
            """)
            for r in cur.fetchall():
                row = self.table.rowCount()
                self.table.insertRow(row)
                for col, v in enumerate([
                    r["month"], str(r["cnt"]),
                    f"{float(r['total']):,.2f} ₽",
                ]):
                    self.table.setItem(row, col, QTableWidgetItem(v))

    def _load_reconciliation(self):
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(
            ["Тур", "Договоров", "Сумма по договорам", "Оплачено"]
        )
        self.table.setRowCount(0)
        conn = Database.connect()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    t.title,
                    COUNT(DISTINCT c.id) AS contracts_cnt,
                    COALESCE(SUM(c.total), 0) AS contract_sum,
                    COALESCE((
                        SELECT SUM(p.amount)
                        FROM payments p
                        JOIN contracts c2 ON c2.id = p.contract_id
                        WHERE c2.tour_id = t.id AND p.status = 'paid'
                    ), 0) AS paid_sum
                FROM tours t
                LEFT JOIN contracts c ON c.tour_id = t.id
                GROUP BY t.id, t.title
                ORDER BY t.title
            """)
            for r in cur.fetchall():
                row = self.table.rowCount()
                self.table.insertRow(row)
                for col, v in enumerate([
                    r["title"], str(r["contracts_cnt"]),
                    f"{float(r['contract_sum']):,.2f} ₽",
                    f"{float(r['paid_sum']):,.2f} ₽",
                ]):
                    self.table.setItem(row, col, QTableWidgetItem(v))