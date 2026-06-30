import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.rbac import Role
from app.models.user import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_active_by_supabase_user_id(self, supabase_user_id: uuid.UUID) -> User | None:
        statement = (
            select(User)
            .where(User.supabase_user_id == supabase_user_id)
            .where(User.deleted_at.is_(None))
            .where(User.is_active.is_(True))
        )
        return self._db.execute(statement).scalar_one_or_none()

    def get_active_by_id(self, user_id: uuid.UUID) -> User | None:
        statement = (
            select(User)
            .where(User.id == user_id)
            .where(User.deleted_at.is_(None))
            .where(User.is_active.is_(True))
        )
        return self._db.execute(statement).scalar_one_or_none()

    def get_active_by_email(self, email: str) -> User | None:
        statement = (
            select(User)
            .where(User.email == email.lower())
            .where(User.deleted_at.is_(None))
            .where(User.is_active.is_(True))
        )
        return self._db.execute(statement).scalar_one_or_none()

    def get_role_name(self, role_id: uuid.UUID) -> str:
        statement = select(Role.name).where(Role.id == role_id)
        role_name = self._db.execute(statement).scalar_one_or_none()
        if role_name is None:
            raise ValueError("User role is not configured")
        return role_name
