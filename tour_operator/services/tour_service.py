from repositories.tour_repo import TourRepository
from models.entities import Tour


class TourService:
    def __init__(self):
        self.repo = TourRepository()

    def list_tours(self) -> list[Tour]:
        return [self._to_model(r) for r in self.repo.all()]

    def search(self, value: str) -> list[Tour]:
        return [self._to_model(r) for r in self.repo.search("title", value)]

    def save(self, tour: Tour) -> int:
        data = {
            "title":        tour.title,
            "direction_id": tour.direction_id,
            "hotel_id":     tour.hotel_id,
            "date_start":   tour.date_start,
            "date_end":     tour.date_end,
            "price":        tour.price,
            "quota":        tour.quota,
            "status":       tour.status,
        }
        if tour.id is None:
            return self.repo.insert(data)
        self.repo.update(tour.id, data)
        return tour.id

    def delete(self, pk: int) -> None:
        self.repo.delete(pk)

    @staticmethod
    def _to_model(row: dict) -> Tour:
        return Tour(
            id=row["id"],
            title=row["title"],
            direction_id=row["direction_id"],
            hotel_id=row["hotel_id"],
            date_start=row["date_start"],
            date_end=row["date_end"],
            price=float(row["price"]),
            quota=row["quota"],
            status=row["status"],
        )