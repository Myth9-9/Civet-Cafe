from __future__ import annotations

import uuid
from decimal import Decimal
import pytest

from app.models.menu import Category, MenuItem
from app.services.menu import CategoryService, MenuItemService, MenuValidationError, MenuNotFoundError
from app.schemas.menu import CategoryCreate, CategoryUpdate, MenuItemCreate, MenuItemUpdate


def test_create_category_succeeds(db):
    service = CategoryService(db)
    payload = CategoryCreate(
        name="Hot Drinks",
        description="Warm beverages",
        display_order=1,
        is_active=True,
    )
    category = service.create(payload)

    assert category.name == "Hot Drinks"
    assert category.description == "Warm beverages"
    assert category.display_order == 1
    assert category.is_active is True
    assert category.id is not None


def test_create_category_duplicate_name_raises_error(db):
    # Seed a category
    category = Category(
        id=uuid.uuid4(),
        name="Desserts",
        display_order=2,
    )
    db.add(category)
    db.commit()

    service = CategoryService(db)
    payload = CategoryCreate(name="Desserts")
    
    with pytest.raises(MenuValidationError) as exc_info:
        service.create(payload)
    assert "name already exists" in str(exc_info.value)


def test_update_category(db):
    category_id = uuid.uuid4()
    category = Category(
        id=category_id,
        name="Bakery",
        display_order=3,
        is_active=True,
    )
    db.add(category)
    db.commit()

    service = CategoryService(db)
    payload = CategoryUpdate(name="Breads & Cakes", display_order=5)
    updated = service.update(category_id, payload)

    assert updated.name == "Breads & Cakes"
    assert updated.display_order == 5


def test_delete_category_soft_delete(db):
    category_id = uuid.uuid4()
    category = Category(
        id=category_id,
        name="Ice Creams",
        display_order=4,
    )
    db.add(category)
    db.commit()

    service = CategoryService(db)
    service.delete(category_id)

    # Verify soft deleted
    deleted_category = db.get(Category, category_id)
    assert deleted_category.deleted_at is not None
    
    # Category should not appear in list of categories anymore
    categories = service.list(include_inactive=True, limit=10, offset=0)
    assert len([c for c in categories if c.id == category_id]) == 0


def test_create_menu_item(db):
    category_id = uuid.uuid4()
    category = Category(
        id=category_id,
        name="Coffee",
        display_order=1,
    )
    db.add(category)
    db.commit()

    service = MenuItemService(db)
    payload = MenuItemCreate(
        category_id=category_id,
        sku="LATTE-01",
        name="Caffe Latte",
        description="Espresso with steamed milk",
        price=Decimal("150.00"),
        tax_rate=Decimal("5.00"),
        is_available=True,
        display_order=1,
    )
    item = service.create(payload)

    assert item.name == "Caffe Latte"
    assert item.sku == "LATTE-01"
    assert item.price == Decimal("150.00")
    assert item.tax_rate == Decimal("5.00")
    assert item.category_id == category_id


def test_create_menu_item_duplicate_sku_raises_error(db):
    category_id = uuid.uuid4()
    category = Category(id=category_id, name="Coffee", display_order=1)
    db.add(category)
    
    existing_item = MenuItem(
        id=uuid.uuid4(),
        category_id=category_id,
        sku="ESP-01",
        name="Espresso",
        price=Decimal("100.00"),
        tax_rate=Decimal("5.00"),
    )
    db.add(existing_item)
    db.commit()

    service = MenuItemService(db)
    payload = MenuItemCreate(
        category_id=category_id,
        sku="ESP-01", # Duplicate SKU
        name="Double Espresso",
        price=Decimal("120.00"),
        tax_rate=Decimal("5.00"),
    )
    
    with pytest.raises(MenuValidationError) as exc_info:
        service.create(payload)
    assert "SKU already exists" in str(exc_info.value)


def test_update_menu_item(db):
    category_id = uuid.uuid4()
    category = Category(id=category_id, name="Tea", display_order=2)
    db.add(category)
    
    item_id = uuid.uuid4()
    item = MenuItem(
        id=item_id,
        category_id=category_id,
        sku="TEA-01",
        name="Green Tea",
        price=Decimal("80.00"),
        tax_rate=Decimal("5.00"),
    )
    db.add(item)
    db.commit()

    service = MenuItemService(db)
    payload = MenuItemUpdate(name="Matcha Green Tea", price=Decimal("95.00"))
    updated = service.update(item_id, payload)

    assert updated.name == "Matcha Green Tea"
    assert updated.price == Decimal("95.00")


def test_delete_menu_item_soft_delete(db):
    category_id = uuid.uuid4()
    category = Category(id=category_id, name="Drinks", display_order=3)
    db.add(category)
    
    item_id = uuid.uuid4()
    item = MenuItem(
        id=item_id,
        category_id=category_id,
        sku="COKE-01",
        name="Coke",
        price=Decimal("50.00"),
        tax_rate=Decimal("5.00"),
    )
    db.add(item)
    db.commit()

    service = MenuItemService(db)
    service.delete(item_id)

    # Verify soft deleted
    deleted_item = db.get(MenuItem, item_id)
    assert deleted_item.deleted_at is not None
    assert deleted_item.is_available is False

    # Should not appear in normal list
    items = service.list(category_id=None, include_unavailable=True, limit=10, offset=0)
    assert len([i for i in items if i.id == item_id]) == 0


class TestCategoryEdgeCases:
    def test_update_category_not_found_raises_error(self, db):
        service = CategoryService(db)
        with pytest.raises(MenuNotFoundError):
            service.update(uuid.uuid4(), CategoryUpdate(name="Ghost"))

    def test_delete_category_not_found_raises_error(self, db):
        service = CategoryService(db)
        with pytest.raises(MenuNotFoundError):
            service.delete(uuid.uuid4())

    def test_list_categories_with_pagination(self, db):
        for i in range(5):
            db.add(Category(id=uuid.uuid4(), name=f"Cat-{i}", display_order=i, is_active=True))
        db.commit()

        service = CategoryService(db)
        page1 = service.list(include_inactive=False, limit=2, offset=0)
        assert len(page1) == 2
        page2 = service.list(include_inactive=False, limit=2, offset=2)
        assert len(page2) == 2

    def test_list_categories_offset_pagination(self, db):
        for i in range(10):
            db.add(Category(id=uuid.uuid4(), name=f"Cat-{i:02d}", display_order=i, is_active=True))
        db.commit()

        service = CategoryService(db)
        all_cats = service.list(include_inactive=False, limit=10, offset=0)
        assert len(all_cats) == 10
        no_more = service.list(include_inactive=False, limit=10, offset=10)
        assert len(no_more) == 0


class TestMenuItemEdgeCases:
    def test_update_menu_item_not_found_raises_error(self, db):
        service = MenuItemService(db)
        with pytest.raises(MenuNotFoundError):
            service.update(uuid.uuid4(), MenuItemUpdate(name="Ghost"))

    def test_delete_menu_item_not_found_raises_error(self, db):
        service = MenuItemService(db)
        with pytest.raises(MenuNotFoundError):
            service.delete(uuid.uuid4())

    def test_list_menu_items_filters_by_category(self, db):
        cat_a = Category(id=uuid.uuid4(), name="Cat A", display_order=1)
        cat_b = Category(id=uuid.uuid4(), name="Cat B", display_order=2)
        db.add_all([cat_a, cat_b])
        db.add(MenuItem(id=uuid.uuid4(), category_id=cat_a.id, sku="A-01", name="Item A", price=Decimal("10"), tax_rate=Decimal("5")))
        db.add(MenuItem(id=uuid.uuid4(), category_id=cat_b.id, sku="B-01", name="Item B", price=Decimal("10"), tax_rate=Decimal("5")))
        db.commit()

        service = MenuItemService(db)
        items_a = service.list(category_id=cat_a.id, include_unavailable=True, limit=10, offset=0)
        assert len(items_a) == 1
        assert items_a[0].name == "Item A"

    def test_list_menu_items_pagination(self, db):
        cat = Category(id=uuid.uuid4(), name="Cat", display_order=1)
        db.add(cat)
        for i in range(5):
            db.add(MenuItem(id=uuid.uuid4(), category_id=cat.id, sku=f"SKU-{i:03d}", name=f"Item {i}", price=Decimal("10"), tax_rate=Decimal("5")))
        db.commit()

        service = MenuItemService(db)
        page1 = service.list(category_id=None, include_unavailable=True, limit=2, offset=0)
        assert len(page1) == 2
        page2 = service.list(category_id=None, include_unavailable=True, limit=2, offset=2)
        assert len(page2) == 2
