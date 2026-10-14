from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QComboBox, QSpinBox,
    QTextEdit, QDialogButtonBox
)


class FeedbackForm(QDialog):
    def __init__(self, tours: list[dict], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Обратная связь")
        self.setMinimumWidth(400)

        form = QFormLayout(self)

        self.source = QComboBox()
        self.source.addItems(["client", "partner"])
        form.addRow("Источник:", self.source)

        self.author = QLineEdit()
        self.author.setPlaceholderText("ФИО клиента или название партнёра")
        form.addRow("Автор:", self.author)

        self.tour = QComboBox()
        self.tour.addItem("— без привязки к туру —", None)
        for t in tours:
            self.tour.addItem(f"#{t['id']} {t['title']}", t["id"])
        form.addRow("Тур:", self.tour)

        self.rating = QSpinBox()
        self.rating.setRange(1, 5)
        self.rating.setValue(5)
        form.addRow("Оценка (1–5):", self.rating)

        self.comment = QTextEdit()
        self.comment.setFixedHeight(80)
        self.comment.setPlaceholderText("Комментарий...")
        form.addRow("Комментарий:", self.comment)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def get_data(self) -> dict:
        return {
            "source":  self.source.currentText(),
            "author":  self.author.text().strip(),
            "tour_id": self.tour.currentData(),
            "rating":  self.rating.value(),
            "comment": self.comment.toPlainText().strip(),
        }