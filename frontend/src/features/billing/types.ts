export type BillStatus = "issued" | "paid" | "void";
export type PaymentMethod = "cash" | "card" | "upi" | "wallet" | "mixed";
export type PaymentStatus = "pending" | "completed" | "failed" | "refunded";

export type Payment = {
  id: string;
  billId: string;
  method: PaymentMethod;
  status: PaymentStatus;
  amount: string;
  referenceNumber: string | null;
};

export type Bill = {
  id: string;
  billNumber: string;
  orderId: string;
  issuedByUserId: string;
  status: BillStatus;
  gstin: string | null;
  customerName: string | null;
  customerPhone: string | null;
  subtotalAmount: string;
  taxAmount: string;
  discountAmount: string;
  totalAmount: string;
  roundedTotalAmount: string;
  payments: Payment[];
};

export type ReceiptLine = {
  name: string;
  quantity: number;
  unitPrice: string;
  taxRate: string;
  lineSubtotal: string;
  lineTax: string;
  lineTotal: string;
};

export type Receipt = {
  bill: Bill;
  orderNumber: string;
  tableId: string | null;
  lines: ReceiptLine[];
  paidAmount: string;
  balanceDue: string;
};

