"""Окно сопровождения туров."""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QLabel,
    QInputDialog
)

from services.tour_service import TourService
from services.incident_service import IncidentService
from ui.forms.incident_form import IncidentForm
from ui.forms.resolve_incident_form import ResolveIncidentForm
from db.database import Database


class GuideWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.tour_service = TourService()
        self.incident_service = IncidentService()

        self.setWindowTitle(f"Сопровождение туров — {user.full_name}")
        self.resize(1050, 620)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        menu_bar = QHBoxLayout()
        for name in ("Мои туры", "Инциденты", "Отчёты"):
            btn = QPushButton(name)
            btn.clicked.connect(lambda _, n=name: self._switch_section(n))
            menu_bar.addWidget(btn)
        root.addLayout(menu_bar)

        toolbar = QHBoxLayout()
        self.btn_add = QPushButton("Добавить")
        self.btn_add.clicked.connect(self._on_add)
        toolbar.addWidget(self.btn_add)

        self.btn_edit = QPushButton("Действие")
        self.btn_edit.clicked.connect(self._on_action)
        toolbar.addWidget(self.btn_edit)

        self.btn_del = QPushButton("Удалить")
        self.btn_del.clicked.connect(self._on_delete)
        toolbar.addWidget(self.btn_del)
        root.addLayout(toolbar)

        self.table = QTableWidget(0, 5)
        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        root.addWidget(self.table)

        self.section_label = QLabel("Раздел: Мои туры")
        root.addWidget(self.section_label)

        self.current_section = "Мои туры"
        self._switch_section("Мои туры")

    def _switch_section(self, name: str):
        self.current_section = name
        self.section_label.setText(f"Раздел: {name}")
        if name == "Мои туры":
            self._load_tours()
        elif name == "Инциденты":
            self._load_incidents()
        elif name == "Отчёты":
            self._load_reports()

    def _load_tours(self):
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Тур", "Начало", "Окончание"]
        )
        self.table.setRowCount(0)
        tours = [t for t in self.tour_service.list_tours()
                 if t.status == "Активен"]
        for t in tours:
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col, v in enumerate([
                str(t.id), t.title,
                t.date_start.isoformat(), t.date_end.isoformat(),
            ]):
                self.table.setItem(row, col, QTableWidgetItem(v))

    def _load_incidents(self):
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Тур", "Заголовок", "Тип",
             "Важность", "Статус", "Решение"]
        )
        self.table.setRowCount(0)
        for i in self.incident_service.list_all():
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col, v in enumerate([
                str(i["id"]), i["tour_title"], i["title"],
                i["incident_type"], i["severity"], i["status"],
                i.get("solution") or "—",
            ]):
                self.table.setItem(row, col, QTableWidgetItem(str(v)))

    def _load_reports(self):
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(
            ["Тур", "Всего инцидентов", "Решено"]
        )
        self.table.setRowCount(0)
        conn = Database.connect()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT t.title,
                       COUNT(i.id) AS total,
                       COUNT(i.id) FILTER (WHERE i.status IN
                           ('resolved','closed')) AS resolved
                FROM tours t
                LEFT JOIN incidents i ON i.tour_id = t.id
                GROUP BY t.id, t.title
                ORDER BY t.title
            """)
            for r in cur.fetchall():
                row = self.table.rowCount()
                self.table.insertRow(row)
                for col, v in enumerate([
                    r["title"], str(r["total"]), str(r["resolved"]),
                ]):
                    self.table.setItem(row, col, QTableWidgetItem(v))

    def _selected_id(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return None
        return int(self.table.item(rows[0].row(), 0).text())

    def _on_add(self):
        if self.current_section == "Инциденты":
            tours = [{"id": t.id, "title": t.title}
                     for t in self.tour_service.list_tours()]
            dlg = IncidentForm(tours, parent=self)
            if dlg.exec():
                d = dlg.get_data()
                if not d["title"]:
                    QMessageBox.warning(
                        self, "Инцидент", "Укажите заголовок"
                    )
                    return
                self.incident_service.add(
                    d["tour_id"], d["title"], d["description"],
                    d["incident_type"], d["severity"], self.user.id
                )
                self._load_incidents()
        else:
            QMessageBox.information(
                self, "Добавить",
                "Добавление доступно в разделе Инциденты"
            )

    def _on_action(self):
        pk = self._selected_id()
        if pk is None:
            QMessageBox.information(self, "Действие", "Выберите строку")
            return
        if self.current_section == "Инциденты":
            choice, ok = QInputDialog.getItem(
                self, "Действие с инцидентом", "Что сделать:",
                ["Назначить на себя", "Решить"],
                editable=False
            )
            if not ok:
                return
            if choice == "Назначить на себя":
                self.incident_service.assign(pk, self.user.id)
                self._load_incidents()
            elif choice == "Решить":
                dlg = ResolveIncidentForm("Решение", parent=self)
                if dlg.exec():
                    sol = dlg.get_solution()
                    if not sol:
                        QMessageBox.warning(
                            self, "Решение", "Введите решение"
                        )
                        return
                    self.incident_service.resolve(pk, sol)
                    self._load_incidents()
        else:
            QMessageBox.information(
                self, "Действие", "В этом разделе недоступно"
            )

    def _on_delete(self):
        pk = self._selected_id()
        if pk is None:
            QMessageBox.information(self, "Удалить", "Выберите строку")
            return
        if self.current_section == "Инциденты":
            if QMessageBox.question(
                self, "Удалить", f"Удалить инцидент id={pk}?"
            ) == QMessageBox.StandardButton.Yes:
                self.incident_service.delete(pk)
                self._load_incidents()
        else:
            QMessageBox.information(
                self, "Удалить", "В этом разделе недоступно"
            )