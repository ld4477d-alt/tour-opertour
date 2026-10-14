from repositories.audit_repo import AuditRepository


class AuditService:
    def __init__(self):
        self.repo = AuditRepository()

    def log(self, user_id, action, entity=None,
            entity_id=None, details=None) -> None:
        self.repo.log(user_id, action, entity, entity_id, details)

    def list_all(self):
        return self.repo.list_with_user()