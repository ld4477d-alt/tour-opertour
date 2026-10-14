from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QComboBox, QDoubleSpinBox, QDialogButtonBox
)


class PaymentForm(QDialog):
    METHODS = ["card", "cash", "transfer"]
    STATUSES = ["paid", "pending", "refunded"]

    def __init__(self, contracts: list[dict], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Новая оплата")
        self.setMinimumWidth(420)

        form = QFormLayout(self)

        self.contract = QComboBox()
        for c in contracts:
            label = f"№{c['id']} | {c['client_name']} | {c['tour_title']}"
            self.contract.addItem(label, c["id"])
        form.addRow("Договор:", self.contract)

        self.amount = QDoubleSpinBox()
        self.amount.setMaximum(10_000_000)
        self.amount.setValue(0)
        form.addRow("Сумма:", self.amount)

        self.method = QComboBox()
        self.method.addItems(self.METHODS)
        form.addRow("Способ:", self.method)

        self.status = QComboBox()
        self.status.addItems(self.STATUSES)
        form.addRow("Статус:", self.status)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def get_data(self) -> dict:
        return {
            "contract_id": self.contract.currentData(),
            "amount":      self.amount.value(),
            "method":      self.method.currentText(),
            "status":      self.status.currentText(),
        }