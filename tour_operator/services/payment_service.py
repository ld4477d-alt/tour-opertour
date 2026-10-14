from repositories.payment_repo import PaymentRepository


class PaymentService:
    def __init__(self):
        self.repo = PaymentRepository()

    def list_all(self):
        return self.repo.list_with_contract()

    def add(self, contract_id: int, amount: float,
            method: str = "card", status: str = "paid") -> int:
        return self.repo.insert({
            "contract_id": contract_id,
            "amount":      amount,
            "method":      method,
            "status":      status,
        })

    def delete(self, pk: int) -> None:
        self.repo.delete(pk)

    def total_paid(self) -> float:
        return self.repo.total_paid()