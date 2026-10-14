from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QComboBox,
    QTextEdit, QDialogButtonBox
)


class IncidentForm(QDialog):
    TYPES = ["other", "hotel", "transport", "health", "documents"]
    SEVERITIES = ["low", "normal", "high", "critical"]

    def __init__(self, tours: list[dict], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Новый инцидент")
        self.setMinimumWidth(420)

        form = QFormLayout(self)

        self.tour = QComboBox()
        for t in tours:
            self.tour.addItem(f"#{t['id']} {t['title']}", t["id"])
        form.addRow("Тур:", self.tour)

        self.title = QLineEdit()
        self.title.setPlaceholderText("Краткое описание проблемы")
        form.addRow("Заголовок:", self.title)

        self.itype = QComboBox()
        self.itype.addItems(self.TYPES)
        form.addRow("Тип:", self.itype)

        self.severity = QComboBox()
        self.severity.addItems(self.SEVERITIES)
        self.severity.setCurrentText("normal")
        form.addRow("Важность:", self.severity)

        self.description = QTextEdit()
        self.description.setFixedHeight(100)
        form.addRow("Описание:", self.description)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def get_data(self) -> dict:
        return {
            "tour_id":       self.tour.currentData(),
            "title":         self.title.text().strip(),
            "incident_type": self.itype.currentText(),
            "severity":      self.severity.currentText(),
            "description":   self.description.toPlainText().strip(),
        }