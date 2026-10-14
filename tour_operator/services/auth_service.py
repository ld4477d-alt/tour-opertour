import hashlib
from repositories.user_repo import UserRepository
from models.entities import User


class AuthService:
    def __init__(self):
        self.users = UserRepository()

    @staticmethod
    def _hash(password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def login(self, username: str, password: str) -> User | None:
        row = self.users.find_by_username(username)
        if not row or not row["is_active"]:
            return None
        if row["password_hash"] != password and \
           row["password_hash"] != self._hash(password):
            return None
        return User(
            id=row["id"],
            username=row["username"],
            full_name=row["full_name"],
            role=row["role"],
        )

    def list_users(self) -> list[dict]:
        """Список активных пользователей для окна входа."""
        return self.users.list_active()