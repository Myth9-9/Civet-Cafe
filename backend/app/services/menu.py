import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.menu import Category, MenuItem
from app.repositories.menu import CategoryRepository, MenuItemRepository
from app.schemas.menu import CategoryCreate, CategoryUpdate, MenuItemCreate, MenuItemUpdate


class MenuValidationError(ValueError):
    pass


class MenuNotFoundError(ValueError):
    pass


class CategoryService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._categories = CategoryRepository(db)

    def list(self, *, include_inactive: bool, limit: int, offset: int) -> list[Category]:
        return list(self._categories.list(include_inactive=include_inactive, limit=limit, offset=offset))

    def create(self, payload: CategoryCreate) -> Category:
        normalized_name = payload.name.strip()
        if self._categories.get_by_name(normalized_name):
            raise MenuValidationError("Category name already exists")
        category = self._categories.add(
            Category(
                name=normalized_name,
                description=payload.description,
                display_order=payload.display_order,
                is_active=payload.is_active,
            )
        )
        self._db.commit()
        self._db.refresh(category)
        return category

    def update(self, category_id: uuid.UUID, payload: CategoryUpdate) -> Category:
        category = self._require_category(category_id)
        update_data = payload.model_dump(exclude_unset=True)
        if "name" in update_data and update_data["name"] is not None:
            normalized_name = update_data["name"].strip()
            existing = self._categories.get_by_name(normalized_name)
            if existing and existing.id != category_id:
                raise MenuValidationError("Category name already exists")
            category.name = normalized_name
        for field in ("description", "display_order", "is_active"):
            if field in update_data:
                setattr(category, field, update_data[field])
        self._db.commit()
        self._db.refresh(category)
        return category

    def delete(self, category_id: uuid.UUID) -> None:
        category = self._require_category(category_id)
        category.deleted_at = datetime.now(UTC)
        category.is_active = False
        self._db.commit()

    def _require_category(self, category_id: uuid.UUID) -> Category:
        category = self._categories.get_active(category_id)
        if category is None:
            raise MenuNotFoundError("Category not found")
        return category


class MenuItemService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._categories = CategoryRepository(db)
        self._items = MenuItemRepository(db)

    def list(
        self,
        *,
        category_id: uuid.UUID | None,
        include_unavailable: bool,
        limit: int,
        offset: int,
    ) -> list[MenuItem]:
        return list(
            self._items.list(
                category_id=category_id,
                include_unavailable=include_unavailable,
                limit=limit,
                offset=offset,
            )
        )

    def create(self, payload: MenuItemCreate) -> MenuItem:
        self._validate_category(payload.category_id)
        normalized_sku = payload.sku.strip().upper()
        if self._items.get_by_sku(normalized_sku):
            raise MenuValidationError("Menu item SKU already exists")
        item = self._items.add(
            MenuItem(
                category_id=payload.category_id,
                sku=normalized_sku,
                name=payload.name.strip(),
                description=payload.description,
                price=payload.price,
                tax_rate=payload.tax_rate,
                is_available=payload.is_available,
                display_order=payload.display_order,
            )
        )
        self._db.commit()
        self._db.refresh(item)
        return item

    def update(self, item_id: uuid.UUID, payload: MenuItemUpdate) -> MenuItem:
        item = self._require_item(item_id)
        update_data = payload.model_dump(exclude_unset=True)
        if "category_id" in update_data and update_data["category_id"] is not None:
            self._validate_category(update_data["category_id"])
        if "sku" in update_data and update_data["sku"] is not None:
            normalized_sku = update_data["sku"].strip().upper()
            existing = self._items.get_by_sku(normalized_sku)
            if existing and existing.id != item_id:
                raise MenuValidationError("Menu item SKU already exists")
            item.sku = normalized_sku
        if "name" in update_data and update_data["name"] is not None:
            item.name = update_data["name"].strip()
        for field in (
            "category_id",
            "description",
            "price",
            "tax_rate",
            "is_available",
            "display_order",
        ):
            if field in update_data:
                setattr(item, field, update_data[field])
        self._db.commit()
        self._db.refresh(item)
        return item

    def delete(self, item_id: uuid.UUID) -> None:
        item = self._require_item(item_id)
        item.deleted_at = datetime.now(UTC)
        item.is_available = False
        self._db.commit()

    def _validate_category(self, category_id: uuid.UUID) -> None:
        category = self._categories.get_active(category_id)
        if category is None or not category.is_active:
            raise MenuValidationError("Category is not available")

    def _require_item(self, item_id: uuid.UUID) -> MenuItem:
        item = self._items.get_active(item_id)
        if item is None:
            raise MenuNotFoundError("Menu item not found")
        return item

