import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.rbac import Permission, Role
from app.models.setting import Setting
from app.models.user import User


class AdminUserRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list_users(self, *, include_inactive: bool, limit: int, offset: int) -> Sequence[User]:
        statement = (
            select(User)
            .where(User.deleted_at.is_(None))
            .order_by(User.full_name)
            .limit(limit)
            .offset(offset)
        )
        if not include_inactive:
            statement = statement.where(User.is_active.is_(True))
        return self._db.execute(statement).scalars().all()

    def get_user(self, user_id: uuid.UUID) -> User | None:
        statement = select(User).where(User.id == user_id).where(User.deleted_at.is_(None))
        return self._db.execute(statement).scalar_one_or_none()

    def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email).where(User.deleted_at.is_(None))
        return self._db.execute(statement).scalar_one_or_none()

    def get_by_employee_code(self, employee_code: str) -> User | None:
        statement = (
            select(User)
            .where(User.employee_code == employee_code)
            .where(User.deleted_at.is_(None))
        )
        return self._db.execute(statement).scalar_one_or_none()

    def add_user(self, user: User) -> User:
        self._db.add(user)
        self._db.flush()
        return user

    def list_roles(self) -> Sequence[Role]:
        return self._db.execute(select(Role).order_by(Role.name)).scalars().all()

    def get_role(self, role_id: uuid.UUID) -> Role | None:
        return self._db.get(Role, role_id)

    def list_permissions(self) -> Sequence[Permission]:
        return self._db.execute(select(Permission).order_by(Permission.module, Permission.action)).scalars().all()


class SettingsRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list(self, *, public_only: bool) -> Sequence[Setting]:
        statement = select(Setting).order_by(Setting.key)
        if public_only:
            statement = statement.where(Setting.is_public.is_(True))
        return self._db.execute(statement).scalars().all()

    def get_by_key(self, key: str) -> Setting | None:
        return self._db.execute(select(Setting).where(Setting.key == key)).scalar_one_or_none()

    def add(self, setting: Setting) -> Setting:
        self._db.add(setting)
        self._db.flush()
        return setting

