from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QComboBox,
    QTextEdit, QDialogButtonBox
)


class RecommendationForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Рекомендация для закупок")
        self.setMinimumWidth(420)

        form = QFormLayout(self)

        self.title = QLineEdit()
        self.title.setPlaceholderText("Коротко: о чём рекомендация")
        form.addRow("Заголовок:", self.title)

        self.priority = QComboBox()
        self.priority.addItems(["low", "normal", "high"])
        self.priority.setCurrentText("normal")
        form.addRow("Приоритет:", self.priority)

        self.body = QTextEdit()
        self.body.setFixedHeight(120)
        form.addRow("Текст:", self.body)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def get_data(self) -> dict:
        return {
            "title":    self.title.text().strip(),
            "body":     self.body.toPlainText().strip(),
            "priority": self.priority.currentText(),
        }