from repositories.feedback_repo import FeedbackRepository


class FeedbackService:
    def __init__(self):
        self.repo = FeedbackRepository()

    def list_all(self):
        return self.repo.list_with_tour()

    def add(self, source: str, author: str, tour_id: int | None,
            rating: int, comment: str) -> int:
        return self.repo.insert({
            "source":      source,
            "author_name": author,
            "tour_id":     tour_id,
            "rating":      rating,
            "comment":     comment,
        })

    def delete(self, pk: int) -> None:
        self.repo.delete(pk)

    def avg_rating(self) -> float:
        return self.repo.avg_rating()