"""Окно отдела аналитики."""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QLabel
)

from services.feedback_service import FeedbackService
from services.recommendation_service import RecommendationService
from ui.forms.feedback_form import FeedbackForm
from ui.forms.recommendation_form import RecommendationForm
from services.tour_service import TourService
from db.database import Database


class AnalystWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.feedback_service = FeedbackService()
        self.rec_service = RecommendationService()
        self.tour_service = TourService()

        self.setWindowTitle(f"Аналитика — {user.full_name}")
        self.resize(1050, 620)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        menu_bar = QHBoxLayout()
        for name in ("Продажи", "Обратная связь", "Рекомендации"):
            btn = QPushButton(name)
            btn.clicked.connect(lambda _, n=name: self._switch_section(n))
            menu_bar.addWidget(btn)
        root.addLayout(menu_bar)

        toolbar = QHBoxLayout()
        self.btn_add = QPushButton("Добавить")
        self.btn_add.clicked.connect(self._on_add)
        toolbar.addWidget(self.btn_add)

        self.btn_del = QPushButton("Удалить")
        self.btn_del.clicked.connect(self._on_delete)
        toolbar.addWidget(self.btn_del)

        self.btn_refresh = QPushButton("Обновить")
        self.btn_refresh.clicked.connect(self._refresh)
        toolbar.addWidget(self.btn_refresh)
        root.addLayout(toolbar)

        self.table = QTableWidget(0, 4)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        root.addWidget(self.table)

        self.section_label = QLabel("Раздел: Продажи")
        root.addWidget(self.section_label)

        self.current_section = "Продажи"
        self._switch_section("Продажи")

    def _switch_section(self, name: str):
        self.current_section = name
        self.section_label.setText(f"Раздел: {name}")
        self._refresh()

    def _refresh(self):
        if self.current_section == "Продажи":
            self._load_sales()
        elif self.current_section == "Обратная связь":
            self._load_feedback()
        elif self.current_section == "Рекомендации":
            self._load_recommendations()

    def _load_sales(self):
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(
            ["Тур", "Продаж", "Сумма", "Средний чек"]
        )
        self.table.setRowCount(0)
        conn = Database.connect()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT t.title,
                       COUNT(c.id) AS cnt,
                       COALESCE(SUM(c.total), 0) AS total,
                       COALESCE(AVG(c.total), 0) AS avg_ch
                FROM tours t
                LEFT JOIN contracts c ON c.tour_id = t.id
                GROUP BY t.id, t.title
                ORDER BY cnt DESC
            """)
            for r in cur.fetchall():
                row = self.table.rowCount()
                self.table.insertRow(row)
                for col, v in enumerate([
                    r["title"], str(r["cnt"]),
                    f"{float(r['total']):.2f}",
                    f"{float(r['avg_ch']):.2f}",
                ]):
                    self.table.setItem(row, col, QTableWidgetItem(v))

    def _load_feedback(self):
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Источник", "Автор", "Тур", "Оценка"]
        )
        self.table.setRowCount(0)
        for f in self.feedback_service.list_all():
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col, v in enumerate([
                str(f["id"]), f["source"], f["author_name"],
                f.get("tour_title") or "—", str(f["rating"]),
            ]):
                self.table.setItem(row, col, QTableWidgetItem(str(v)))

    def _load_recommendations(self):
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Заголовок", "Приоритет", "Статус", "Автор", "Дата"]
        )
        self.table.setRowCount(0)
        for r in self.rec_service.list_all():
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col, v in enumerate([
                str(r["id"]), r["title"], r["priority"], r["status"],
                r.get("author_name") or "—",
                str(r["created_at"])[:19],
            ]):
                self.table.setItem(row, col, QTableWidgetItem(str(v)))

    def _selected_id(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return None
        return int(self.table.item(rows[0].row(), 0).text())

    def _on_add(self):
        if self.current_section == "Обратная связь":
            tours = [{"id": t.id, "title": t.title}
                     for t in self.tour_service.list_tours()]
            dlg = FeedbackForm(tours, parent=self)
            if dlg.exec():
                d = dlg.get_data()
                if not d["author"]:
                    QMessageBox.warning(self, "ОС", "Укажите автора")
                    return
                self.feedback_service.add(**d)
                self._load_feedback()
        elif self.current_section == "Рекомендации":
            dlg = RecommendationForm(parent=self)
            if dlg.exec():
                d = dlg.get_data()
                if not d["title"] or not d["body"]:
                    QMessageBox.warning(
                        self, "Рекомендации",
                        "Заголовок и текст обязательны"
                    )
                    return
                self.rec_service.add(
                    d["title"], d["body"], d["priority"], self.user.id
                )
                self._load_recommendations()
        else:
            QMessageBox.information(
                self, "Добавить",
                "Здесь добавление не предусмотрено"
            )

    def _on_delete(self):
        pk = self._selected_id()
        if pk is None:
            QMessageBox.information(self, "Удалить", "Выберите строку")
            return
        if self.current_section == "Обратная связь":
            self.feedback_service.delete(pk)
            self._load_feedback()
        elif self.current_section == "Рекомендации":
            self.rec_service.delete(pk)
            self._load_recommendations()
        else:
            QMessageBox.information(
                self, "Удалить",
                "В этом разделе удаление не предусмотрено"
            )