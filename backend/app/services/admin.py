import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.setting import Setting
from app.models.user import User
from app.repositories.admin import AdminUserRepository, SettingsRepository
from app.schemas.settings import SettingUpdate, SettingUpsert
from app.schemas.users import UserCreate, UserUpdate


class AdminValidationError(ValueError):
    pass


class AdminNotFoundError(ValueError):
    pass


class UserAdminService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = AdminUserRepository(db)

    def list_users(self, *, include_inactive: bool, limit: int, offset: int) -> list[User]:
        return list(self._repo.list_users(include_inactive=include_inactive, limit=limit, offset=offset))

    def list_roles(self):
        return list(self._repo.list_roles())

    def list_permissions(self):
        return list(self._repo.list_permissions())

    def create_user(self, payload: UserCreate) -> User:
        email = str(payload.email).lower()
        self._ensure_role(payload.role_id)
        if self._repo.get_by_email(email):
            raise AdminValidationError("User email already exists")
        if payload.employee_code and self._repo.get_by_employee_code(payload.employee_code):
            raise AdminValidationError("Employee code already exists")
        user = self._repo.add_user(
            User(
                email=email,
                full_name=payload.full_name.strip(),
                role_id=payload.role_id,
                supabase_user_id=payload.supabase_user_id,
                phone=payload.phone,
                employee_code=payload.employee_code,
                is_active=payload.is_active,
            )
        )
        self._db.commit()
        self._db.refresh(user)
        return user

    def update_user(self, user_id: uuid.UUID, payload: UserUpdate) -> User:
        user = self._require_user(user_id)
        update_data = payload.model_dump(exclude_unset=True)
        if "role_id" in update_data and update_data["role_id"] is not None:
            self._ensure_role(update_data["role_id"])
        if "employee_code" in update_data and update_data["employee_code"]:
            existing = self._repo.get_by_employee_code(update_data["employee_code"])
            if existing and existing.id != user_id:
                raise AdminValidationError("Employee code already exists")
        for field, value in update_data.items():
            if field == "full_name" and value is not None:
                value = value.strip()
            setattr(user, field, value)
        self._db.commit()
        self._db.refresh(user)
        return user

    def delete_user(self, user_id: uuid.UUID) -> None:
        user = self._require_user(user_id)
        user.deleted_at = datetime.now(UTC)
        user.is_active = False
        self._db.commit()

    def _ensure_role(self, role_id: uuid.UUID) -> None:
        if self._repo.get_role(role_id) is None:
            raise AdminValidationError("Role does not exist")

    def _require_user(self, user_id: uuid.UUID) -> User:
        user = self._repo.get_user(user_id)
        if user is None:
            raise AdminNotFoundError("User not found")
        return user


class SettingsService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = SettingsRepository(db)

    def list(self, *, public_only: bool) -> list[Setting]:
        return list(self._repo.list(public_only=public_only))

    def upsert(self, payload: SettingUpsert) -> Setting:
        key = payload.key.strip().lower()
        setting = self._repo.get_by_key(key)
        if setting is None:
            setting = self._repo.add(Setting(key=key, value=payload.value, is_public=payload.is_public))
        else:
            setting.value = payload.value
            setting.is_public = payload.is_public
        self._db.commit()
        self._db.refresh(setting)
        return setting

    def update(self, key: str, payload: SettingUpdate) -> Setting:
        setting = self._repo.get_by_key(key.strip().lower())
        if setting is None:
            raise AdminNotFoundError("Setting not found")
        update_data = payload.model_dump(exclude_unset=True)
        if "value" in update_data and update_data["value"] is not None:
            setting.value = update_data["value"]
        if "is_public" in update_data and update_data["is_public"] is not None:
            setting.is_public = update_data["is_public"]
        self._db.commit()
        self._db.refresh(setting)
        return setting

