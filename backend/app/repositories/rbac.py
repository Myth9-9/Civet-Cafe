import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.rbac import Permission, RolePermission


class RolePermissionRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list_permission_codes_for_role(self, role_id: uuid.UUID) -> list[str]:
        statement = (
            select(Permission.code)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .where(RolePermission.role_id == role_id)
            .order_by(Permission.code)
        )
        return list(self._db.execute(statement).scalars().all())

