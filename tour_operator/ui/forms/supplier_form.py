from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QComboBox, QDialogButtonBox
)


class SupplierForm(QDialog):
    KINDS = ["hotel", "transport", "guide"]

    def __init__(self, supplier: dict | None = None, parent=None):
        super().__init__(parent)
        self.supplier = supplier
        self.setWindowTitle("Поставщик")
        self.setMinimumWidth(360)

        form = QFormLayout(self)

        self.name = QLineEdit(supplier["name"] if supplier else "")
        form.addRow("Название:", self.name)

        self.kind = QComboBox()
        self.kind.addItems(self.KINDS)
        if supplier:
            self.kind.setCurrentText(supplier["kind"])
        form.addRow("Тип:", self.kind)

        self.city = QLineEdit(supplier["city"] if supplier else "")
        form.addRow("Город:", self.city)

        self.contact = QLineEdit(supplier["contact"] if supplier else "")
        form.addRow("Контактное лицо:", self.contact)

        self.phone = QLineEdit(supplier["phone"] if supplier else "")
        form.addRow("Телефон:", self.phone)

        self.email = QLineEdit(supplier["email"] if supplier else "")
        form.addRow("Email:", self.email)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def get_data(self) -> dict:
        return {
            "name":    self.name.text().strip(),
            "kind":    self.kind.currentText(),
            "city":    self.city.text().strip(),
            "contact": self.contact.text().strip(),
            "phone":   self.phone.text().strip(),
            "email":   self.email.text().strip(),
        }