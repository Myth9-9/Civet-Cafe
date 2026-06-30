"""Seed the database with default roles, permissions, and an admin user.

Usage:
    python scripts/seed.py

Requires DATABASE_URL in the environment or a .env file in the backend root.
"""

import uuid

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.db.base import Base
from app.models.rbac import Permission, Role, RolePermission
from app.models.user import User

PERMISSIONS: list[dict[str, str]] = [
    {"code": "menu.read", "module": "menu", "action": "read"},
    {"code": "menu.write", "module": "menu", "action": "write"},
    {"code": "orders.read", "module": "orders", "action": "read"},
    {"code": "orders.write", "module": "orders", "action": "write"},
    {"code": "billing.read", "module": "billing", "action": "read"},
    {"code": "billing.write", "module": "billing", "action": "write"},
    {"code": "tables.read", "module": "tables", "action": "read"},
    {"code": "tables.write", "module": "tables", "action": "write"},
    {"code": "reports.read", "module": "reports", "action": "read"},
    {"code": "admin.read", "module": "admin", "action": "read"},
    {"code": "admin.write", "module": "admin", "action": "write"},
    {"code": "settings.read", "module": "settings", "action": "read"},
    {"code": "settings.write", "module": "settings", "action": "write"},
]

CASHIER_PERMISSION_CODES: set[str] = {
    "menu.read",
    "orders.read",
    "orders.write",
    "tables.read",
    "tables.write",
    "billing.read",
    "billing.write",
    "reports.read",
}


def _get_or_create_permissions(db: Session) -> dict[str, Permission]:
    from sqlalchemy import select

    created: dict[str, Permission] = {}
    for pdef in PERMISSIONS:
        stmt = select(Permission).where(Permission.code == pdef["code"])
        existing = db.execute(stmt).scalar_one_or_none()
        if existing:
            created[pdef["code"]] = existing
        else:
            perm = Permission(id=uuid.uuid4(), **pdef)
            db.add(perm)
            db.flush()
            created[pdef["code"]] = perm
    return created


def _get_or_create_role(
    db: Session, name: str, description: str, is_system: bool = False
) -> Role:
    from sqlalchemy import select

    existing = db.execute(select(Role).where(Role.name == name)).scalar_one_or_none()
    if existing:
        return existing
    role = Role(id=uuid.uuid4(), name=name, description=description, is_system=is_system)
    db.add(role)
    db.flush()
    return role


def _link_permissions(
    db: Session, role_id: uuid.UUID, permissions: dict[str, Permission]
) -> None:
    for _code, perm in permissions.items():
        stmt = text(
            "SELECT 1 FROM role_permissions "
            "WHERE role_id = :role_id AND permission_id = :perm_id"
        )
        existing = db.execute(stmt, {"role_id": role_id, "perm_id": perm.id}).scalar_one_or_none()
        if not existing:
            db.add(RolePermission(id=uuid.uuid4(), role_id=role_id, permission_id=perm.id))


def seed() -> None:
    settings = get_settings()
    if not settings.database_url:
        msg = (
            "DATABASE_URL must be configured. "
            "Run with a .env file or set the environment variable."
        )
        raise RuntimeError(msg)

    engine = create_engine(settings.database_url, pool_pre_ping=True)
    Base.metadata.create_all(bind=engine)

    session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    db = session_local()

    try:
        permissions = _get_or_create_permissions(db)
        print(f"Seeded {len(permissions)} permissions")

        admin_role = _get_or_create_role(db, "admin", "System Administrator", is_system=True)
        cashier_role = _get_or_create_role(db, "cashier", "Cashier Staff")

        _link_permissions(db, admin_role.id, permissions)

        cashier_perms = {k: v for k, v in permissions.items() if k in CASHIER_PERMISSION_CODES}
        _link_permissions(db, cashier_role.id, cashier_perms)

        db.commit()
        print(
            f"Linked permissions to roles: "
            f"admin ({len(permissions)}), "
            f"cashier ({len(CASHIER_PERMISSION_CODES)})"
        )

        from sqlalchemy import select as sa_select

        existing_admin = db.execute(
            sa_select(User).where(User.email == "admin@civetcafe.com")
        ).scalar_one_or_none()
        if existing_admin is None:
            admin_user = User(
                id=uuid.uuid4(),
                role_id=admin_role.id,
                email="admin@civetcafe.com",
                full_name="Admin",
                employee_code="ADMIN-001",
                is_active=True,
            )
            db.add(admin_user)
            db.commit()
            print("Created default admin user: admin@civetcafe.com")
        else:
            print("Admin user already exists, skipping")

        print("\nSeed complete!")

    finally:
        db.close()
        engine.dispose()


if __name__ == "__main__":
    seed()
