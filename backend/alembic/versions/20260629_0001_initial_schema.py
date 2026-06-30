"""Initial Civet Cafe POS schema.

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-06-29
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


table_status = postgresql.ENUM(
    "available",
    "occupied",
    "reserved",
    "inactive",
    name="table_status",
    create_type=False,
)
order_status = postgresql.ENUM(
    "draft",
    "placed",
    "preparing",
    "ready",
    "served",
    "cancelled",
    "billed",
    name="order_status",
    create_type=False,
)
bill_status = postgresql.ENUM("issued", "paid", "void", name="bill_status", create_type=False)
payment_method = postgresql.ENUM(
    "cash",
    "card",
    "upi",
    "wallet",
    "mixed",
    name="payment_method",
    create_type=False,
)
payment_status = postgresql.ENUM(
    "pending",
    "completed",
    "failed",
    "refunded",
    name="payment_status",
    create_type=False,
)


def uuid_pk() -> sa.Column[sa.UUID]:
    return sa.Column(
        "id",
        postgresql.UUID(as_uuid=True),
        primary_key=True,
        server_default=sa.text("gen_random_uuid()"),
    )


def timestamps() -> list[sa.Column[sa.DateTime]]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    ]


def soft_delete() -> sa.Column[sa.DateTime]:
    return sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True)


def create_updated_at_trigger(table_name: str) -> None:
    op.execute(
        sa.text(
            f"""
            CREATE TRIGGER trg_{table_name}_updated_at
            BEFORE UPDATE ON {table_name}
            FOR EACH ROW
            EXECUTE FUNCTION set_updated_at();
            """
        )
    )


def drop_updated_at_trigger(table_name: str) -> None:
    op.execute(sa.text(f"DROP TRIGGER IF EXISTS trg_{table_name}_updated_at ON {table_name};"))


def upgrade() -> None:
    op.execute(sa.text('CREATE EXTENSION IF NOT EXISTS "pgcrypto";'))
    op.execute(
        sa.text(
            """
            CREATE OR REPLACE FUNCTION set_updated_at()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = NOW();
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
            """
        )
    )

    bind = op.get_bind()
    for enum_type in (table_status, order_status, bill_status, payment_method, payment_status):
        enum_type.create(bind, checkfirst=True)

    op.create_table(
        "roles",
        uuid_pk(),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_system", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        *timestamps(),
        sa.UniqueConstraint("name", name="uq_roles_name"),
    )

    op.create_table(
        "permissions",
        uuid_pk(),
        sa.Column("code", sa.String(length=120), nullable=False),
        sa.Column("module", sa.String(length=80), nullable=False),
        sa.Column("action", sa.String(length=80), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        *timestamps(),
        sa.UniqueConstraint("code", name="uq_permissions_code"),
    )
    op.create_index("ix_permissions_module_action", "permissions", ["module", "action"])

    op.create_table(
        "role_permissions",
        uuid_pk(),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("permission_id", postgresql.UUID(as_uuid=True), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["permission_id"], ["permissions.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("role_id", "permission_id", name="uq_role_permissions_role_permission"),
    )
    op.create_index("ix_role_permissions_role_id", "role_permissions", ["role_id"])
    op.create_index("ix_role_permissions_permission_id", "role_permissions", ["permission_id"])

    op.create_table(
        "users",
        uuid_pk(),
        sa.Column("supabase_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=160), nullable=False),
        sa.Column("phone", sa.String(length=32), nullable=True),
        sa.Column("employee_code", sa.String(length=40), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        *timestamps(),
        soft_delete(),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("supabase_user_id", name="uq_users_supabase_user_id"),
        sa.UniqueConstraint("email", name="uq_users_email"),
        sa.UniqueConstraint("employee_code", name="uq_users_employee_code"),
    )
    op.create_index("ix_users_role_id", "users", ["role_id"])
    op.create_index("ix_users_email_active", "users", ["email", "is_active"])
    op.create_index("ix_users_deleted_at", "users", ["deleted_at"])

    op.create_table(
        "categories",
        uuid_pk(),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        *timestamps(),
        soft_delete(),
        sa.UniqueConstraint("name", name="uq_categories_name"),
    )
    op.create_index("ix_categories_active_order", "categories", ["is_active", "display_order"])
    op.create_index("ix_categories_deleted_at", "categories", ["deleted_at"])

    op.create_table(
        "menu_items",
        uuid_pk(),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sku", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("price", sa.Numeric(12, 2), nullable=False),
        sa.Column("tax_rate", sa.Numeric(5, 2), nullable=False, server_default=sa.text("5.00")),
        sa.Column("is_available", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default=sa.text("0")),
        *timestamps(),
        soft_delete(),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("sku", name="uq_menu_items_sku"),
    )
    op.create_index("ix_menu_items_category_id", "menu_items", ["category_id"])
    op.create_index("ix_menu_items_available_order", "menu_items", ["is_available", "display_order"])
    op.create_index("ix_menu_items_deleted_at", "menu_items", ["deleted_at"])

    op.create_table(
        "tables",
        uuid_pk(),
        sa.Column("table_number", sa.String(length=40), nullable=False),
        sa.Column("floor", sa.String(length=80), nullable=False, server_default=sa.text("'Main'")),
        sa.Column("capacity", sa.Integer(), nullable=False),
        sa.Column("status", table_status, nullable=False, server_default=sa.text("'available'")),
        *timestamps(),
        soft_delete(),
        sa.UniqueConstraint("floor", "table_number", name="uq_tables_floor_table_number"),
    )
    op.create_index("ix_tables_status", "tables", ["status"])
    op.create_index("ix_tables_floor", "tables", ["floor"])
    op.create_index("ix_tables_deleted_at", "tables", ["deleted_at"])

    op.create_table(
        "orders",
        uuid_pk(),
        sa.Column("order_number", sa.String(length=40), nullable=False),
        sa.Column("table_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_by_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", order_status, nullable=False, server_default=sa.text("'draft'")),
        sa.Column("subtotal_amount", sa.Numeric(12, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("tax_amount", sa.Numeric(12, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("discount_amount", sa.Numeric(12, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("total_amount", sa.Numeric(12, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("notes", sa.Text(), nullable=True),
        *timestamps(),
        sa.ForeignKeyConstraint(["table_id"], ["tables.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("order_number", name="uq_orders_order_number"),
    )
    op.create_index("ix_orders_table_id", "orders", ["table_id"])
    op.create_index("ix_orders_created_by_user_id", "orders", ["created_by_user_id"])
    op.create_index("ix_orders_status_created_at", "orders", ["status", "created_at"])
    op.create_index("ix_orders_created_at", "orders", ["created_at"])

    op.create_table(
        "order_items",
        uuid_pk(),
        sa.Column("order_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("menu_item_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("item_name_snapshot", sa.String(length=160), nullable=False),
        sa.Column("unit_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("tax_rate", sa.Numeric(5, 2), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("line_subtotal", sa.Numeric(12, 2), nullable=False),
        sa.Column("line_tax", sa.Numeric(12, 2), nullable=False),
        sa.Column("line_total", sa.Numeric(12, 2), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        *timestamps(),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["menu_item_id"], ["menu_items.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_order_items_order_id", "order_items", ["order_id"])
    op.create_index("ix_order_items_menu_item_id", "order_items", ["menu_item_id"])

    op.create_table(
        "bills",
        uuid_pk(),
        sa.Column("bill_number", sa.String(length=40), nullable=False),
        sa.Column("order_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("issued_by_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", bill_status, nullable=False, server_default=sa.text("'issued'")),
        sa.Column("gstin", sa.String(length=32), nullable=True),
        sa.Column("customer_name", sa.String(length=160), nullable=True),
        sa.Column("customer_phone", sa.String(length=32), nullable=True),
        sa.Column("subtotal_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("tax_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("discount_amount", sa.Numeric(12, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("total_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("rounded_total_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("voided_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("void_reason", sa.Text(), nullable=True),
        *timestamps(),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["issued_by_user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("bill_number", name="uq_bills_bill_number"),
        sa.UniqueConstraint("order_id", name="uq_bills_order_id"),
    )
    op.create_index("ix_bills_order_id", "bills", ["order_id"])
    op.create_index("ix_bills_issued_by_user_id", "bills", ["issued_by_user_id"])
    op.create_index("ix_bills_status_created_at", "bills", ["status", "created_at"])
    op.create_index("ix_bills_created_at", "bills", ["created_at"])

    op.create_table(
        "payments",
        uuid_pk(),
        sa.Column("bill_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("method", payment_method, nullable=False),
        sa.Column("status", payment_status, nullable=False, server_default=sa.text("'pending'")),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("reference_number", sa.String(length=120), nullable=True),
        sa.Column("provider_response", sa.Text(), nullable=True),
        *timestamps(),
        sa.ForeignKeyConstraint(["bill_id"], ["bills.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_payments_bill_id", "payments", ["bill_id"])
    op.create_index("ix_payments_method_status", "payments", ["method", "status"])
    op.create_index("ix_payments_created_at", "payments", ["created_at"])

    op.create_table(
        "settings",
        uuid_pk(),
        sa.Column("key", sa.String(length=120), nullable=False),
        sa.Column("value", postgresql.JSONB(), nullable=False),
        sa.Column("is_public", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        *timestamps(),
        sa.UniqueConstraint("key", name="uq_settings_key"),
    )
    op.create_index("ix_settings_key", "settings", ["key"])
    op.create_index("ix_settings_public", "settings", ["is_public"])

    op.create_table(
        "audit_logs",
        uuid_pk(),
        sa.Column("actor_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("action", sa.String(length=120), nullable=False),
        sa.Column("entity_type", sa.String(length=120), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("before_data", postgresql.JSONB(), nullable=True),
        sa.Column("after_data", postgresql.JSONB(), nullable=True),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        *timestamps(),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_audit_logs_actor_user_id", "audit_logs", ["actor_user_id"])
    op.create_index("ix_audit_logs_entity", "audit_logs", ["entity_type", "entity_id"])
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"])

    for table_name in (
        "roles",
        "permissions",
        "role_permissions",
        "users",
        "categories",
        "menu_items",
        "tables",
        "orders",
        "order_items",
        "bills",
        "payments",
        "settings",
        "audit_logs",
    ):
        create_updated_at_trigger(table_name)


def downgrade() -> None:
    table_names = (
        "audit_logs",
        "settings",
        "payments",
        "bills",
        "order_items",
        "orders",
        "tables",
        "menu_items",
        "categories",
        "users",
        "role_permissions",
        "permissions",
        "roles",
    )

    for table_name in table_names:
        drop_updated_at_trigger(table_name)

    for table_name in table_names:
        op.drop_table(table_name)

    bind = op.get_bind()
    for enum_type in (payment_status, payment_method, bill_status, order_status, table_status):
        enum_type.drop(bind, checkfirst=True)

    op.execute(sa.text("DROP FUNCTION IF EXISTS set_updated_at();"))
