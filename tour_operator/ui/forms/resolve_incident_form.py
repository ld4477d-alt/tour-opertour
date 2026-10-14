from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QTextEdit, QDialogButtonBox, QLabel
)


class ResolveIncidentForm(QDialog):
    def __init__(self, incident_title: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Решение инцидента")
        self.setMinimumWidth(420)

        form = QFormLayout(self)

        title_label = QLabel(incident_title)
        title_label.setWordWrap(True)
        form.addRow("Инцидент:", title_label)

        self.solution = QTextEdit()
        self.solution.setFixedHeight(120)
        self.solution.setPlaceholderText(
            "Опишите, что было сделано для решения..."
        )
        form.addRow("Решение:", self.solution)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def get_solution(self) -> str:
        return self.solution.toPlainText().strip()