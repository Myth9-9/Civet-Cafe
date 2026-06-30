import uuid
from datetime import UTC, datetime
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.orm import Session

from app.models.menu import MenuItem
from app.models.order import Order, OrderItem, OrderStatus
from app.models.table import CafeTable, TableStatus
from app.repositories.orders import OrderItemRepository, OrderRepository
from app.schemas.orders import AddOrderItemRequest, OrderCreate, OrderItemCreate, UpdateOrderItemRequest


class OrderValidationError(ValueError):
    pass


class OrderNotFoundError(ValueError):
    pass


ALLOWED_TRANSITIONS: dict[OrderStatus, set[OrderStatus]] = {
    OrderStatus.DRAFT: {OrderStatus.PLACED, OrderStatus.CANCELLED},
    OrderStatus.PLACED: {OrderStatus.PREPARING, OrderStatus.CANCELLED},
    OrderStatus.PREPARING: {OrderStatus.READY, OrderStatus.CANCELLED},
    OrderStatus.READY: {OrderStatus.SERVED, OrderStatus.CANCELLED},
    OrderStatus.SERVED: {OrderStatus.BILLED},
    OrderStatus.CANCELLED: set(),
    OrderStatus.BILLED: set(),
}


class OrderService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._orders = OrderRepository(db)
        self._items = OrderItemRepository(db)

    def list(
        self,
        *,
        status: OrderStatus | None,
        table_id: uuid.UUID | None,
        limit: int,
        offset: int,
    ) -> list[Order]:
        return list(self._orders.list(status=status, table_id=table_id, limit=limit, offset=offset))

    def get(self, order_id: uuid.UUID) -> Order:
        return self._require_order(order_id)

    def create(self, *, payload: OrderCreate, created_by_user_id: uuid.UUID) -> Order:
        table = self._validate_table(payload.table_id) if payload.table_id else None
        order = self._orders.add(
            Order(
                order_number=self._next_order_number(),
                table_id=payload.table_id,
                created_by_user_id=created_by_user_id,
                status=OrderStatus.DRAFT,
                notes=payload.notes,
            )
        )
        for item_payload in payload.items:
            self._add_item(order, item_payload)
        self._recalculate(order)
        if table is not None:
            table.status = TableStatus.OCCUPIED
        self._db.commit()
        self._db.refresh(order)
        return self._require_order(order.id)

    def add_item(self, order_id: uuid.UUID, payload: AddOrderItemRequest) -> Order:
        order = self._require_mutable_order(order_id)
        self._add_item(order, payload)
        self._recalculate(order)
        self._db.commit()
        return self._require_order(order.id)

    def update_item(
        self,
        *,
        order_id: uuid.UUID,
        item_id: uuid.UUID,
        payload: UpdateOrderItemRequest,
    ) -> Order:
        order = self._require_mutable_order(order_id)
        item = self._require_order_item(order, item_id)
        update_data = payload.model_dump(exclude_unset=True)
        if "quantity" in update_data:
            item.quantity = update_data["quantity"]
        if "notes" in update_data:
            item.notes = update_data["notes"]
        self._recalculate_item(item)
        self._recalculate(order)
        self._db.commit()
        return self._require_order(order.id)

    def remove_item(self, *, order_id: uuid.UUID, item_id: uuid.UUID) -> Order:
        order = self._require_mutable_order(order_id)
        item = self._require_order_item(order, item_id)
        order.items.remove(item)
        self._items.delete(item)
        self._recalculate(order)
        self._db.commit()
        self._db.refresh(order)
        return self._require_order(order.id)

    def transition(self, order_id: uuid.UUID, next_status: OrderStatus) -> Order:
        order = self._require_order(order_id)
        if next_status == order.status:
            return order
        if next_status not in ALLOWED_TRANSITIONS[order.status]:
            raise OrderValidationError(f"Cannot transition order from {order.status} to {next_status}")
        if next_status == OrderStatus.PLACED and not order.items:
            raise OrderValidationError("Cannot place an order without items")
        order.status = next_status
        if order.table_id and next_status in {OrderStatus.CANCELLED, OrderStatus.BILLED}:
            table = self._db.get(CafeTable, order.table_id)
            if table is not None:
                table.status = TableStatus.AVAILABLE
        self._db.commit()
        return self._require_order(order.id)

    def _add_item(self, order: Order, payload: OrderItemCreate) -> OrderItem:
        menu_item = self._validate_menu_item(payload.menu_item_id)
        item = self._items.add(
            OrderItem(
                order_id=order.id,
                menu_item_id=menu_item.id,
                item_name_snapshot=menu_item.name,
                unit_price=menu_item.price,
                tax_rate=menu_item.tax_rate,
                quantity=payload.quantity,
                line_subtotal=Decimal("0.00"),
                line_tax=Decimal("0.00"),
                line_total=Decimal("0.00"),
                notes=payload.notes,
            )
        )
        self._recalculate_item(item)
        order.items.append(item)
        return item

    def _recalculate_item(self, item: OrderItem) -> None:
        subtotal = Decimal(item.quantity) * item.unit_price
        tax = subtotal * item.tax_rate / Decimal("100")
        item.line_subtotal = self._money(subtotal)
        item.line_tax = self._money(tax)
        item.line_total = self._money(subtotal + tax)

    def _recalculate(self, order: Order) -> None:
        subtotal = sum((item.line_subtotal for item in order.items), Decimal("0.00"))
        tax = sum((item.line_tax for item in order.items), Decimal("0.00"))
        discount = order.discount_amount or Decimal("0.00")
        order.subtotal_amount = self._money(subtotal)
        order.tax_amount = self._money(tax)
        order.discount_amount = self._money(discount)
        order.total_amount = self._money(subtotal + tax - discount)

    def _validate_menu_item(self, menu_item_id: uuid.UUID) -> MenuItem:
        menu_item = self._db.get(MenuItem, menu_item_id)
        if menu_item is None or menu_item.deleted_at is not None or not menu_item.is_available:
            raise OrderValidationError("Menu item is not available")
        return menu_item

    def _validate_table(self, table_id: uuid.UUID) -> CafeTable:
        table = self._db.get(CafeTable, table_id)
        if table is None or table.deleted_at is not None or table.status == TableStatus.INACTIVE:
            raise OrderValidationError("Table is not available")
        if table.status == TableStatus.OCCUPIED:
            raise OrderValidationError("Table is already occupied")
        return table

    def _require_order(self, order_id: uuid.UUID) -> Order:
        order = self._orders.get(order_id)
        if order is None:
            raise OrderNotFoundError("Order not found")
        return order

    def _require_mutable_order(self, order_id: uuid.UUID) -> Order:
        order = self._require_order(order_id)
        if order.status not in {OrderStatus.DRAFT, OrderStatus.PLACED}:
            raise OrderValidationError("Order can no longer be edited")
        return order

    def _require_order_item(self, order: Order, item_id: uuid.UUID) -> OrderItem:
        for item in order.items:
            if item.id == item_id:
                return item
        raise OrderNotFoundError("Order item not found")

    def _next_order_number(self) -> str:
        prefix = datetime.now(UTC).strftime("ORD-%Y%m%d-")
        for sequence in range(1, 10000):
            candidate = f"{prefix}{sequence:04d}"
            if self._orders.get_by_number(candidate) is None:
                return candidate
        raise OrderValidationError("Order sequence exhausted for today")

    def _money(self, value: Decimal) -> Decimal:
        return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

