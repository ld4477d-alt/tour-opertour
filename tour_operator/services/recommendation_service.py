from repositories.recommendation_repo import RecommendationRepository


class RecommendationService:
    def __init__(self):
        self.repo = RecommendationRepository()

    def list_all(self):
        return self.repo.list_with_author()

    def add(self, title: str, body: str, priority: str,
            author_id: int) -> int:
        return self.repo.insert({
            "title":     title,
            "body":      body,
            "priority":  priority,
            "status":    "new",
            "author_id": author_id,
        })

    def update_status(self, pk: int, status: str) -> None:
        self.repo.update(pk, {"status": status})

    def delete(self, pk: int) -> None:
        self.repo.delete(pk)