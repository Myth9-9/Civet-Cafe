import enum

from sqlalchemy import Enum, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, enum_values
from app.models.mixins import SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin


class TableStatus(str, enum.Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    RESERVED = "reserved"
    INACTIVE = "inactive"


class CafeTable(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "tables"

    table_number: Mapped[str] = mapped_column(String(40), nullable=False)
    floor: Mapped[str] = mapped_column(String(80), nullable=False, server_default="Main")
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[TableStatus] = mapped_column(
        Enum(
            TableStatus,
            name="table_status",
            values_callable=enum_values,
        ),
        nullable=False,
        server_default=TableStatus.AVAILABLE.value,
    )

    __table_args__ = (
        UniqueConstraint("floor", "table_number", name="uq_tables_floor_table_number"),
        Index("ix_tables_status", "status"),
        Index("ix_tables_floor", "floor"),
        Index("ix_tables_deleted_at", "deleted_at"),
    )

