from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QMessageBox,
    QComboBox, QLineEdit
)
from services.auth_service import AuthService


class LoginWindow(QWidget):
    def __init__(self, on_success):
        super().__init__()
        self.auth = AuthService()
        self.on_success = on_success

        self.setWindowTitle("АС «ТурОператор» — Вход")
        self.setFixedSize(360, 210)

        layout = QVBoxLayout(self)

        # ---- Логин: выпадающий список с возможностью ввода ----
        layout.addWidget(QLabel("Логин:"))

        self.login_combo = QComboBox()
        self.login_combo.setEditable(True)          # можно и выбрать, и ввести
        self.login_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        # Показываем только username в поле, а в списке — ФИО + роль
        self.login_combo.currentIndexChanged.connect(self._on_user_changed)
        layout.addWidget(self.login_combo)

        # ---- Пароль ----
        layout.addWidget(QLabel("Пароль:"))
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.returnPressed.connect(self._login)
        layout.addWidget(self.password_edit)

        # ---- Кнопка ----
        btn = QPushButton("Войти")
        btn.clicked.connect(self._login)
        layout.addWidget(btn)

        self._load_users()

    # ---------- Заполнение выпадающего списка ----------
    def _load_users(self):
        self.login_combo.clear()
        try:
            users = self.auth.list_users()
        except Exception as e:
            QMessageBox.critical(
                self, "Ошибка",
                f"Не удалось загрузить список пользователей:\n{e}"
            )
            return

        if not users:
            QMessageBox.warning(
                self, "Вход", "В базе нет активных пользователей"
            )
            return

        for u in users:
            # Что показываем в выпадающем списке:
            label = f"{u['full_name']} — {u['role']} ({u['username']})"
            # Что реально лежит в поле (username):
            self.login_combo.addItem(label, u["username"])

        # По умолчанию — первый
        self.login_combo.setCurrentIndex(0)
        self._on_user_changed()

    # ---------- При выборе — фокус на пароль ----------
    def _on_user_changed(self):
        self.password_edit.clear()
        self.password_edit.setFocus()

    # ---------- Вход ----------
    def _login(self):
        # Если пользователь выбрал из списка — берём данные из itemData.
        # Если ввёл логин вручную — берём текст поля.
        username = self.login_combo.currentData()
        if not username:
            username = self.login_combo.currentText().strip()

        # Если в поле оказалась длинная подпись (ФИО — роль (логин)),
        # вытащим логин из скобок.
        if "(" in username and username.endswith(")"):
            username = username.rsplit("(", 1)[1].rstrip(")")

        password = self.password_edit.text()

        if not username or not password:
            QMessageBox.warning(self, "Вход", "Введите логин и пароль")
            return

        user = self.auth.login(username, password)
        if user is None:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")
            return
        self.on_success(user)