import { apiClient } from "../../lib/apiClient";
import type { AddOrderItem, Order, OrderCreate, OrderStatus } from "./types";

type ApiOrderItem = {
  id: string;
  order_id: string;
  menu_item_id: string | null;
  item_name_snapshot: string;
  unit_price: string;
  tax_rate: string;
  quantity: number;
  line_subtotal: string;
  line_tax: string;
  line_total: string;
  notes: string | null;
};

type ApiOrder = {
  id: string;
  order_number: string;
  table_id: string | null;
  created_by_user_id: string;
  status: OrderStatus;
  subtotal_amount: string;
  tax_amount: string;
  discount_amount: string;
  total_amount: string;
  notes: string | null;
  items: ApiOrderItem[];
  created_at: string;
  updated_at: string;
};

function mapOrder(order: ApiOrder): Order {
  return {
    id: order.id,
    orderNumber: order.order_number,
    tableId: order.table_id,
    createdByUserId: order.created_by_user_id,
    status: order.status,
    subtotalAmount: order.subtotal_amount,
    taxAmount: order.tax_amount,
    discountAmount: order.discount_amount,
    totalAmount: order.total_amount,
    notes: order.notes,
    createdAt: order.created_at,
    updatedAt: order.updated_at,
    items: order.items.map((item) => ({
      id: item.id,
      orderId: item.order_id,
      menuItemId: item.menu_item_id,
      itemNameSnapshot: item.item_name_snapshot,
      unitPrice: item.unit_price,
      taxRate: item.tax_rate,
      quantity: item.quantity,
      lineSubtotal: item.line_subtotal,
      lineTax: item.line_tax,
      lineTotal: item.line_total,
      notes: item.notes
    }))
  };
}

export async function listOrders(): Promise<Order[]> {
  const { data } = await apiClient.get<ApiOrder[]>("/orders");
  return data.map(mapOrder);
}

export async function createOrder(payload: OrderCreate): Promise<Order> {
  const { data } = await apiClient.post<ApiOrder>("/orders", {
    table_id: payload.tableId || null,
    notes: payload.notes || null,
    items: []
  });
  return mapOrder(data);
}

export async function addOrderItem(orderId: string, payload: AddOrderItem): Promise<Order> {
  const { data } = await apiClient.post<ApiOrder>(`/orders/${orderId}/items`, {
    menu_item_id: payload.menuItemId,
    quantity: payload.quantity,
    notes: payload.notes || null
  });
  return mapOrder(data);
}

export async function transitionOrder(orderId: string, status: OrderStatus): Promise<Order> {
  const { data } = await apiClient.post<ApiOrder>(`/orders/${orderId}/transition`, { status });
  return mapOrder(data);
}

