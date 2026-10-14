"""Окно отдела закупок."""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QMessageBox, QLabel,
    QInputDialog
)

from services.tour_service import TourService
from services.recommendation_service import RecommendationService
from services.supplier_service import SupplierService
from ui.forms.tour_form import TourForm
from ui.forms.supplier_form import SupplierForm
from db.database import Database


class PurchasingWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.tour_service = TourService()
        self.rec_service = RecommendationService()
        self.supplier_service = SupplierService()

        self.setWindowTitle(f"Отдел закупок — {user.full_name}")
        self.resize(1050, 620)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        menu_bar = QHBoxLayout()
        for name in ("Туры", "Рекомендации аналитики", "Поставщики"):
            btn = QPushButton(name)
            btn.clicked.connect(lambda _, n=name: self._switch_section(n))
            menu_bar.addWidget(btn)
        root.addLayout(menu_bar)

        toolbar = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Поиск по турам...")
        toolbar.addWidget(self.search_edit)

        self.btn_search = QPushButton("Поиск")
        self.btn_search.clicked.connect(self._on_search)
        toolbar.addWidget(self.btn_search)

        self.btn_add = QPushButton("Добавить")
        self.btn_add.clicked.connect(self._on_add)
        toolbar.addWidget(self.btn_add)

        self.btn_edit = QPushButton("Изменить")
        self.btn_edit.clicked.connect(self._on_edit)
        toolbar.addWidget(self.btn_edit)

        self.btn_del = QPushButton("Удалить")
        self.btn_del.clicked.connect(self._on_delete)
        toolbar.addWidget(self.btn_del)

        root.addLayout(toolbar)

        self.table = QTableWidget(0, 6)
        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        root.addWidget(self.table)

        self.section_label = QLabel("Раздел: Туры")
        root.addWidget(self.section_label)

        self.current_section = "Туры"
        self._switch_section("Туры")

    def _switch_section(self, name: str):
        self.current_section = name
        self.section_label.setText(f"Раздел: {name}")
        if name == "Туры":
            self._load_tours()
        elif name == "Рекомендации аналитики":
            self._load_recommendations()
        elif name == "Поставщики":
            self._load_suppliers()

    def _load_tours(self):
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Название", "Начало", "Окончание", "Цена", "Статус"]
        )
        self.table.setRowCount(0)
        for t in self.tour_service.list_tours():
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col, v in enumerate([
                str(t.id), t.title,
                t.date_start.isoformat(), t.date_end.isoformat(),
                f"{t.price:.2f}", t.status,
            ]):
                self.table.setItem(row, col, QTableWidgetItem(v))

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

    def _load_suppliers(self):
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Название", "Тип", "Город", "Контакт", "Телефон"]
        )
        self.table.setRowCount(0)
        for s in self.supplier_service.list_all():
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col, v in enumerate([
                str(s["id"]), s["name"], s["kind"],
                s.get("city", ""), s.get("contact", ""),
                s.get("phone", ""),
            ]):
                self.table.setItem(row, col, QTableWidgetItem(v or ""))

    def _selected_id(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return None
        return int(self.table.item(rows[0].row(), 0).text())

    def _on_search(self):
        value = self.search_edit.text().strip()
        if self.current_section != "Туры":
            QMessageBox.information(
                self, "Поиск",
                "Поиск работает только в разделе Туры"
            )
            return
        self.table.setRowCount(0)
        tours = self.tour_service.search(value) if value \
            else self.tour_service.list_tours()
        for t in tours:
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col, v in enumerate([
                str(t.id), t.title,
                t.date_start.isoformat(), t.date_end.isoformat(),
                f"{t.price:.2f}", t.status,
            ]):
                self.table.setItem(row, col, QTableWidgetItem(v))

    def _on_add(self):
        if self.current_section == "Туры":
            dlg = TourForm(parent=self)
            if dlg.exec():
                self.tour_service.save(dlg.get_tour())
                self._load_tours()
        elif self.current_section == "Поставщики":
            dlg = SupplierForm(parent=self)
            if dlg.exec():
                self.supplier_service.save(dlg.get_data())
                self._load_suppliers()
        else:
            QMessageBox.information(
                self, "Добавить",
                "Рекомендации создаёт аналитик"
            )

    def _on_edit(self):
        pk = self._selected_id()
        if pk is None:
            QMessageBox.information(self, "Изменить", "Выберите строку")
            return
        if self.current_section == "Туры":
            row = self.tour_service.repo.get(pk)
            tour = self.tour_service._to_model(row)
            dlg = TourForm(tour, parent=self)
            if dlg.exec():
                self.tour_service.save(dlg.get_tour())
                self._load_tours()
        elif self.current_section == "Рекомендации аналитики":
            status, ok = QInputDialog.getItem(
                self, "Смена статуса", "Новый статус:",
                ["new", "in_work", "done"], editable=False
            )
            if ok:
                self.rec_service.update_status(pk, status)
                self._load_recommendations()
        elif self.current_section == "Поставщики":
            conn = Database.connect()
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM suppliers WHERE id = %s", (pk,))
                s = dict(cur.fetchone())
            dlg = SupplierForm(s, parent=self)
            if dlg.exec():
                self.supplier_service.save(dlg.get_data(), pk)
                self._load_suppliers()

    def _on_delete(self):
        pk = self._selected_id()
        if pk is None:
            QMessageBox.information(self, "Удалить", "Выберите строку")
            return
        if self.current_section == "Туры":
            if QMessageBox.question(
                self, "Удалить", f"Удалить тур id={pk}?"
            ) == QMessageBox.StandardButton.Yes:
                self.tour_service.delete(pk)
                self._load_tours()
        elif self.current_section == "Поставщики":
            if QMessageBox.question(
                self, "Удалить", f"Удалить поставщика id={pk}?"
            ) == QMessageBox.StandardButton.Yes:
                self.supplier_service.delete(pk)
                self._load_suppliers()
        else:
            QMessageBox.information(
                self, "Удалить",
                "В этом разделе удаление не поддерживается"
            )