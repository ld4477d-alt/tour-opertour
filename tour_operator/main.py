import sys
from PyQt6.QtWidgets import QApplication, QMessageBox

from db.database import Database
from ui.login_window import LoginWindow
from ui.main_window import MainWindow
from ui.manager_window import ManagerWindow
from ui.purchasing_window import PurchasingWindow
from ui.analyst_window import AnalystWindow
from ui.guide_window import GuideWindow
from ui.accountant_window import AccountantWindow


ROLE_WINDOWS = {
    "admin":      MainWindow,
    "manager":    ManagerWindow,
    "purchasing": PurchasingWindow,
    "analyst":    AnalystWindow,
    "guide":      GuideWindow,
    "accountant": AccountantWindow,
}


class Application:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.login = LoginWindow(self.show_main)
        self.main = None

    def show_main(self, user):
        WindowClass = ROLE_WINDOWS.get(user.role)
        if WindowClass is None:
            QMessageBox.critical(
                self.login, "Ошибка",
                f"Неизвестная роль: {user.role}"
            )
            return
        self.main = WindowClass(user)
        self.main.show()
        self.login.close()

    def run(self):
        Database.init_schema()
        self.login.show()
        code = self.app.exec()
        Database.close()
        return code


if __name__ == "__main__":
    sys.exit(Application().run())