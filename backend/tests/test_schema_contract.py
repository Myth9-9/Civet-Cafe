from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base
from app.models import (  # noqa: F401
    AuditLog,
    Bill,
    CafeTable,
    Category,
    MenuItem,
    Order,
    OrderItem,
    Payment,
    Permission,
    Role,
    RolePermission,
    Setting,
    User,
)

EXPECTED_TABLES = {
    "audit_logs",
    "bills",
    "categories",
    "menu_items",
    "orders",
    "order_items",
    "payments",
    "permissions",
    "refresh_tokens",
    "role_permissions",
    "roles",
    "settings",
    "tables",
    "users",
}

SOFT_DELETE_TABLES = {
    "categories",
    "menu_items",
    "tables",
    "users",
}


def test_all_required_tables_are_registered() -> None:
    assert set(Base.metadata.tables) == EXPECTED_TABLES


def test_every_table_has_uuid_primary_key_and_timestamps() -> None:
    for table in Base.metadata.sorted_tables:
        primary_key_columns = list(table.primary_key.columns)

        assert len(primary_key_columns) == 1, table.name
        assert primary_key_columns[0].name == "id", table.name
        assert isinstance(primary_key_columns[0].type, UUID), table.name
        assert "created_at" in table.columns, table.name
        assert "updated_at" in table.columns, table.name


def test_soft_delete_tables_have_deleted_at() -> None:
    for table_name in SOFT_DELETE_TABLES:
        assert "deleted_at" in Base.metadata.tables[table_name].columns


def test_core_foreign_keys_are_declared() -> None:
    foreign_keys = {
        (table.name, fk.parent.name, fk.column.table.name, fk.column.name)
        for table in Base.metadata.sorted_tables
        for fk in table.foreign_keys
    }

    assert ("users", "role_id", "roles", "id") in foreign_keys
    assert ("role_permissions", "role_id", "roles", "id") in foreign_keys
    assert ("role_permissions", "permission_id", "permissions", "id") in foreign_keys
    assert ("menu_items", "category_id", "categories", "id") in foreign_keys
    assert ("orders", "table_id", "tables", "id") in foreign_keys
    assert ("orders", "created_by_user_id", "users", "id") in foreign_keys
    assert ("order_items", "order_id", "orders", "id") in foreign_keys
    assert ("bills", "order_id", "orders", "id") in foreign_keys
    assert ("payments", "bill_id", "bills", "id") in foreign_keys
    assert ("audit_logs", "actor_user_id", "users", "id") in foreign_keys
    assert ("refresh_tokens", "user_id", "users", "id") in foreign_keys
