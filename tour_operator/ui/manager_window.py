"""
Кабинет менеджера.

Рабочие функции:
  * каталог туров с фильтром по цене;
  * оформление заявки (создание договора) с проверкой квоты;
  * список заявок с фильтром и сменой статуса.

Заглушки:
  * Клиенты, Оплаты, Отчёты.
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QMessageBox, QLabel,
    QComboBox, QDialog, QFormLayout, QDialogButtonBox, QDoubleSpinBox,
    QDateEdit, QTextEdit
)
from PyQt6.QtCore import QDate

from services.tour_service import TourService
from services.contract_service import ContractService
from db.database import Database


# ---------------------------------------------------------------- диалоги
class ContractDialog(QDialog):
    """Форма оформления заявки: клиент + тур + сумма."""

    def __init__(self, tour_row: dict, parent=None):
        super().__init__(parent)
        self.tour_row = tour_row
        self.setWindowTitle("Оформление заявки")
        self.setMinimumWidth(360)

        form = QFormLayout(self)

        form.addRow("Тур:", QLabel(tour_row["title"]))
        form.addRow("Цена:", QLabel(f"{float(tour_row['price']):.2f} ₽"))
        form.addRow("Доступно мест:", QLabel(str(tour_row["quota"])))

        self.client_name = QLineEdit()
        self.client_name.setPlaceholderText("ФИО клиента")
        form.addRow("Клиент:", self.client_name)

        self.client_phone = QLineEdit()
        self.client_phone.setPlaceholderText("+7 ...")
        form.addRow("Телефон:", self.client_phone)

        self.total_spin = QDoubleSpinBox()
        self.total_spin.setMaximum(10_000_000)
        self.total_spin.setValue(float(tour_row["price"]))
        form.addRow("Сумма договора:", self.total_spin)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def get_data(self) -> dict:
        return {
            "client_name":  self.client_name.text().strip(),
            "client_phone": self.client_phone.text().strip(),
            "total":        self.total_spin.value(),
        }


class ContractDetailsDialog(QDialog):
    """Карточка заявки — только чтение."""

    def __init__(self, contract: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Заявка №{contract['id']}")
        self.setMinimumWidth(420)

        form = QFormLayout(self)

        def add(label: str, value):
            field = QLabel(str(value) if value is not None else "—")
            field.setWordWrap(True)
            form.addRow(label, field)

        add("Номер:",        contract["id"])
        add("Создана:",      contract["created_at"])
        add("Статус:",       contract["status"])
        add("Сумма:",        f"{float(contract['total']):.2f} ₽")
        add("Клиент:",       contract["client_name"])
        add("Телефон:",      contract.get("client_phone"))
        add("Email:",        contract.get("client_email"))
        add("Паспорт:",      contract.get("client_passport"))
        add("Тур:",          contract["tour_title"])
        add("Даты тура:",    f"{contract['tour_start']} — {contract['tour_end']}")
        add("Менеджер:",     contract.get("manager_name"))

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        buttons.accepted.connect(self.accept)
        form.addRow(buttons)


class ChangeStatusDialog(QDialog):
    """Смена статуса заявки."""

    STATUSES = ["Оформлен", "Оплачен", "Отменён"]

    def __init__(self, current: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Смена статуса")
        self.setMinimumWidth(280)

        form = QFormLayout(self)

        self.combo = QComboBox()
        self.combo.addItems(self.STATUSES)
        if current in self.STATUSES:
            self.combo.setCurrentText(current)
        form.addRow("Новый статус:", self.combo)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def get_status(self) -> str:
        return self.combo.currentText()


# ------------------------------------------------------------- главное окно
class ManagerWindow(QMainWindow):
    """Окно менеджера."""

    SECTION_TOURS = "Каталог туров"
    SECTION_CONTRACTS = "Заявки"

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.tour_service = TourService()
        self.contract_service = ContractService()

        self.setWindowTitle(f"Кабинет менеджера — {user.full_name}")
        self.resize(1050, 640)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        # ---------- Меню разделов ----------
        menu_bar = QHBoxLayout()
        for name in (self.SECTION_TOURS, self.SECTION_CONTRACTS,
                     "Клиенты", "Оплаты", "Отчёты"):
            btn = QPushButton(name)
            btn.clicked.connect(lambda _, n=name: self._switch_section(n))
            menu_bar.addWidget(btn)
        root.addLayout(menu_bar)

        # ---------- Общая панель фильтров ----------
        self.filter_widget = QWidget()
        filter_bar = QHBoxLayout(self.filter_widget)
        filter_bar.setContentsMargins(0, 0, 0, 0)

        # Фильтры для туров
        self.tour_filters = QWidget()
        tf = QHBoxLayout(self.tour_filters)
        tf.setContentsMargins(0, 0, 0, 0)
        tf.addWidget(QLabel("Цена от:"))
        self.price_from = QDoubleSpinBox()
        self.price_from.setMaximum(10_000_000)
        tf.addWidget(self.price_from)
        tf.addWidget(QLabel("до:"))
        self.price_to = QDoubleSpinBox()
        self.price_to.setMaximum(10_000_000)
        self.price_to.setValue(10_000_000)
        tf.addWidget(self.price_to)
        tf.addWidget(QLabel("Статус:"))
        self.tour_status_combo = QComboBox()
        self.tour_status_combo.addItems(["Все", "Черновик", "Активен", "Закрыт"])
        tf.addWidget(self.tour_status_combo)
        apply_tour = QPushButton("Применить")
        apply_tour.clicked.connect(self._load_tours)
        tf.addWidget(apply_tour)
        reset_tour = QPushButton("Сброс")
        reset_tour.clicked.connect(self._reset_tour_filter)
        tf.addWidget(reset_tour)

        # Фильтры для заявок
        self.contract_filters = QWidget()
        cf = QHBoxLayout(self.contract_filters)
        cf.setContentsMargins(0, 0, 0, 0)
        cf.addWidget(QLabel("Статус:"))
        self.contract_status_combo = QComboBox()
        self.contract_status_combo.addItems(
            ["Все", "Оформлен", "Оплачен", "Отменён"]
        )
        cf.addWidget(self.contract_status_combo)
        cf.addWidget(QLabel("Дата от:"))
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        cf.addWidget(self.date_from)
        cf.addWidget(QLabel("до:"))
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate().addDays(1))
        cf.addWidget(self.date_to)
        apply_c = QPushButton("Применить")
        apply_c.clicked.connect(self._load_contracts)
        cf.addWidget(apply_c)
        reset_c = QPushButton("Сброс")
        reset_c.clicked.connect(self._reset_contract_filter)
        cf.addWidget(reset_c)

        filter_bar.addWidget(self.tour_filters)
        filter_bar.addWidget(self.contract_filters)
        root.addWidget(self.filter_widget)

        # ---------- Таблица ----------
        self.table = QTableWidget(0, 6)
        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.doubleClicked.connect(self._on_table_double_click)
        root.addWidget(self.table)

        # ---------- Кнопки действий ----------
        self.actions_widget = QWidget()
        actions = QHBoxLayout(self.actions_widget)
        actions.setContentsMargins(0, 0, 0, 0)

        # действия для туров
        self.tour_actions = QWidget()
        ta = QHBoxLayout(self.tour_actions)
        ta.setContentsMargins(0, 0, 0, 0)
        book_btn = QPushButton("Оформить заявку")
        book_btn.clicked.connect(self._on_book)
        ta.addWidget(book_btn)
        refresh_t = QPushButton("Обновить")
        refresh_t.clicked.connect(self._load_tours)
        ta.addWidget(refresh_t)

        # действия для заявок
        self.contract_actions = QWidget()
        ca = QHBoxLayout(self.contract_actions)
        ca.setContentsMargins(0, 0, 0, 0)
        open_btn = QPushButton("Открыть карточку")
        open_btn.clicked.connect(self._on_open_contract)
        ca.addWidget(open_btn)
        status_btn = QPushButton("Изменить статус")
        status_btn.clicked.connect(self._on_change_status)
        ca.addWidget(status_btn)
        refresh_c = QPushButton("Обновить")
        refresh_c.clicked.connect(self._load_contracts)
        ca.addWidget(refresh_c)

        actions.addWidget(self.tour_actions)
        actions.addWidget(self.contract_actions)
        root.addWidget(self.actions_widget)

        self.section_label = QLabel(f"Раздел: {self.SECTION_TOURS}")
        root.addWidget(self.section_label)

        self._switch_section(self.SECTION_TOURS)

    # ---------- Переключение разделов ----------
    def _switch_section(self, name: str):
        self.section_label.setText(f"Раздел: {name}")

        if name == self.SECTION_TOURS:
            self.tour_filters.setVisible(True)
            self.contract_filters.setVisible(False)
            self.tour_actions.setVisible(True)
            self.contract_actions.setVisible(False)
            self._load_tours()

        elif name == self.SECTION_CONTRACTS:
            self.tour_filters.setVisible(False)
            self.contract_filters.setVisible(True)
            self.tour_actions.setVisible(False)
            self.contract_actions.setVisible(True)
            self._load_contracts()

        else:
            self._show_stub(name)

    # ---------- Туры ----------
    def _load_tours(self):
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Название", "Начало", "Окончание", "Цена", "Статус"]
        )
        self.table.setRowCount(0)

        tours = self.tour_service.list_tours()
        pmin = self.price_from.value()
        pmax = self.price_to.value()
        st = self.tour_status_combo.currentText()

        for t in tours:
            if not (pmin <= float(t.price) <= pmax):
                continue
            if st != "Все" and t.status != st:
                continue
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col, v in enumerate([
                str(t.id), t.title,
                t.date_start.isoformat(), t.date_end.isoformat(),
                f"{t.price:.2f}", t.status,
            ]):
                self.table.setItem(row, col, QTableWidgetItem(v))

    def _reset_tour_filter(self):
        self.price_from.setValue(0)
        self.price_to.setValue(10_000_000)
        self.tour_status_combo.setCurrentText("Все")
        self._load_tours()

    def _selected_tour_row(self) -> dict | None:
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return None
        pk = int(self.table.item(rows[0].row(), 0).text())
        return self.tour_service.repo.get(pk)

    def _on_book(self):
        tour = self._selected_tour_row()
        if tour is None:
            QMessageBox.information(self, "Заявка", "Выберите тур")
            return
        if tour["quota"] <= 0:
            QMessageBox.warning(self, "Заявка", "Нет свободных мест")
            return

        dlg = ContractDialog(tour, parent=self)
        if not dlg.exec():
            return
        data = dlg.get_data()
        if not data["client_name"]:
            QMessageBox.warning(self, "Заявка", "Укажите ФИО клиента")
            return

        conn = Database.connect()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO clients (full_name, phone)
                       VALUES (%s, %s) RETURNING id""",
                    (data["client_name"], data["client_phone"]),
                )
                client_id = cur.fetchone()["id"]
                cur.execute(
                    """INSERT INTO contracts
                           (client_id, tour_id, manager_id, status, total)
                       VALUES (%s, %s, %s, 'Оформлен', %s) RETURNING id""",
                    (client_id, tour["id"], self.user.id, data["total"]),
                )
                contract_id = cur.fetchone()["id"]
                cur.execute(
                    """UPDATE tours SET quota = quota - 1
                       WHERE id = %s AND quota > 0""",
                    (tour["id"],),
                )
            conn.commit()
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Ошибка", str(e))
            return

        QMessageBox.information(
            self, "Готово", f"Заявка №{contract_id} оформлена"
        )
        self._load_tours()

    # ---------- Заявки ----------
    def _load_contracts(self):
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Дата", "Клиент", "Тур", "Сумма", "Статус", "Менеджер"]
        )
        self.table.setRowCount(0)

        status = self.contract_status_combo.currentText()
        date_from = self.date_from.date().toString("yyyy-MM-dd")
        date_to = self.date_to.date().toString("yyyy-MM-dd") + " 23:59:59"

        rows = self.contract_service.search(
            status=status if status != "Все" else None,
            date_from=date_from,
            date_to=date_to,
        )

        for c in rows:
            row = self.table.rowCount()
            self.table.insertRow(row)
            values = [
                str(c["id"]),
                str(c["created_at"])[:19],
                c["client_name"],
                c["tour_title"],
                f"{float(c['total']):.2f}",
                c["status"],
                c.get("manager_name") or "—",
            ]
            for col, v in enumerate(values):
                self.table.setItem(row, col, QTableWidgetItem(v))

    def _reset_contract_filter(self):
        self.contract_status_combo.setCurrentText("Все")
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        self.date_to.setDate(QDate.currentDate().addDays(1))
        self._load_contracts()

    def _selected_contract_id(self) -> int | None:
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return None
        try:
            return int(self.table.item(rows[0].row(), 0).text())
        except ValueError:
            return None

    def _on_open_contract(self):
        pk = self._selected_contract_id()
        if pk is None:
            QMessageBox.information(self, "Заявка", "Выберите строку")
            return
        details = self.contract_service.get_details(pk)
        if details is None:
            QMessageBox.warning(self, "Заявка", "Не найдена")
            return
        ContractDetailsDialog(details, parent=self).exec()

    def _on_change_status(self):
        pk = self._selected_contract_id()
        if pk is None:
            QMessageBox.information(self, "Заявка", "Выберите строку")
            return
        details = self.contract_service.get_details(pk)
        if details is None:
            QMessageBox.warning(self, "Заявка", "Не найдена")
            return

        dlg = ChangeStatusDialog(details["status"], parent=self)
        if not dlg.exec():
            return
        new_status = dlg.get_status()
        if new_status == details["status"]:
            return

        try:
            self.contract_service.update_status(pk, new_status)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
            return

        QMessageBox.information(
            self, "Готово",
            f"Статус заявки №{pk} изменён на «{new_status}»"
        )
        self._load_contracts()

    def _on_table_double_click(self, _index):
        # Двойной клик работает только в разделе «Заявки»
        if self.section_label.text().endswith(self.SECTION_CONTRACTS):
            self._on_open_contract()

    # ---------- Заглушки ----------
    def _show_stub(self, name: str):
        self.tour_filters.setVisible(False)
        self.contract_filters.setVisible(False)
        self.tour_actions.setVisible(False)
        self.contract_actions.setVisible(False)

        self.table.setColumnCount(1)
        self.table.setHorizontalHeaderLabels([name])
        self.table.setRowCount(0)
        self.table.insertRow(0)
        self.table.setItem(
            0, 0,
            QTableWidgetItem(f"Раздел «{name}» в разработке")
        )
        QMessageBox.information(self, name, f"Раздел «{name}» в разработке")