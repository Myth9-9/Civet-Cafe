import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.menu import Category, MenuItem


class CategoryRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list(self, *, include_inactive: bool, limit: int, offset: int) -> Sequence[Category]:
        statement = (
            select(Category)
            .where(Category.deleted_at.is_(None))
            .order_by(Category.display_order, Category.name)
            .limit(limit)
            .offset(offset)
        )
        if not include_inactive:
            statement = statement.where(Category.is_active.is_(True))
        return self._db.execute(statement).scalars().all()

    def get_active(self, category_id: uuid.UUID) -> Category | None:
        statement = select(Category).where(Category.id == category_id).where(Category.deleted_at.is_(None))
        return self._db.execute(statement).scalar_one_or_none()

    def get_by_name(self, name: str) -> Category | None:
        statement = (
            select(Category)
            .where(Category.name == name)
            .where(Category.deleted_at.is_(None))
        )
        return self._db.execute(statement).scalar_one_or_none()

    def add(self, category: Category) -> Category:
        self._db.add(category)
        self._db.flush()
        return category


class MenuItemRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list(
        self,
        *,
        category_id: uuid.UUID | None,
        include_unavailable: bool,
        limit: int,
        offset: int,
    ) -> Sequence[MenuItem]:
        statement = (
            select(MenuItem)
            .where(MenuItem.deleted_at.is_(None))
            .order_by(MenuItem.display_order, MenuItem.name)
            .limit(limit)
            .offset(offset)
        )
        if category_id is not None:
            statement = statement.where(MenuItem.category_id == category_id)
        if not include_unavailable:
            statement = statement.where(MenuItem.is_available.is_(True))
        return self._db.execute(statement).scalars().all()

    def get_active(self, item_id: uuid.UUID) -> MenuItem | None:
        statement = select(MenuItem).where(MenuItem.id == item_id).where(MenuItem.deleted_at.is_(None))
        return self._db.execute(statement).scalar_one_or_none()

    def get_by_sku(self, sku: str) -> MenuItem | None:
        statement = select(MenuItem).where(MenuItem.sku == sku).where(MenuItem.deleted_at.is_(None))
        return self._db.execute(statement).scalar_one_or_none()

    def add(self, item: MenuItem) -> MenuItem:
        self._db.add(item)
        self._db.flush()
        return item

