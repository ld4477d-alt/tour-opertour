from repositories.supplier_repo import SupplierRepository


class SupplierService:
    def __init__(self):
        self.repo = SupplierRepository()

    def list_all(self):
        return self.repo.all()

    def save(self, data: dict, pk: int | None = None) -> int:
        if pk is None:
            return self.repo.insert(data)
        self.repo.update(pk, data)
        return pk

    def delete(self, pk: int) -> None:
        self.repo.delete(pk)