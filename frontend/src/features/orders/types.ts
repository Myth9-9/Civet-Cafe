export type OrderStatus =
  | "draft"
  | "placed"
  | "preparing"
  | "ready"
  | "served"
  | "cancelled"
  | "billed";

export type OrderItem = {
  id: string;
  orderId: string;
  menuItemId: string | null;
  itemNameSnapshot: string;
  unitPrice: string;
  taxRate: string;
  quantity: number;
  lineSubtotal: string;
  lineTax: string;
  lineTotal: string;
  notes: string | null;
};

export type Order = {
  id: string;
  orderNumber: string;
  tableId: string | null;
  createdByUserId: string;
  status: OrderStatus;
  subtotalAmount: string;
  taxAmount: string;
  discountAmount: string;
  totalAmount: string;
  notes: string | null;
  items: OrderItem[];
  createdAt: string;
  updatedAt: string;
};

export type OrderCreate = {
  tableId?: string;
  notes?: string;
};

export type AddOrderItem = {
  menuItemId: string;
  quantity: number;
  notes?: string;
};

