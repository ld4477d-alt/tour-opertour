from repositories.incident_repo import IncidentRepository


class IncidentService:
    def __init__(self):
        self.repo = IncidentRepository()

    def list_all(self):
        return self.repo.list_with_tour()

    def add(self, tour_id: int, title: str, description: str,
            incident_type: str, severity: str,
            author_id: int) -> int:
        return self.repo.insert({
            "tour_id":       tour_id,
            "title":         title,
            "description":   description,
            "incident_type": incident_type,
            "severity":      severity,
            "status":        "new",
            "author_id":     author_id,
        })

    def resolve(self, pk: int, solution: str) -> None:
        self.repo.resolve(pk, solution)

    def assign(self, pk: int, user_id: int) -> None:
        self.repo.assign(pk, user_id)

    def delete(self, pk: int) -> None:
        self.repo.delete(pk)