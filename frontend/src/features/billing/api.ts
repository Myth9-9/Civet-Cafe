import { apiClient } from "../../lib/apiClient";
import type { Bill, PaymentMethod, Receipt } from "./types";

type ApiPayment = {
  id: string;
  bill_id: string;
  method: PaymentMethod;
  status: "pending" | "completed" | "failed" | "refunded";
  amount: string;
  reference_number: string | null;
};

type ApiBill = {
  id: string;
  bill_number: string;
  order_id: string;
  issued_by_user_id: string;
  status: "issued" | "paid" | "void";
  gstin: string | null;
  customer_name: string | null;
  customer_phone: string | null;
  subtotal_amount: string;
  tax_amount: string;
  discount_amount: string;
  total_amount: string;
  rounded_total_amount: string;
  payments: ApiPayment[];
};

type ApiReceipt = {
  bill: ApiBill;
  order_number: string;
  table_id: string | null;
  lines: {
    name: string;
    quantity: number;
    unit_price: string;
    tax_rate: string;
    line_subtotal: string;
    line_tax: string;
    line_total: string;
  }[];
  paid_amount: string;
  balance_due: string;
};

function mapBill(bill: ApiBill): Bill {
  return {
    id: bill.id,
    billNumber: bill.bill_number,
    orderId: bill.order_id,
    issuedByUserId: bill.issued_by_user_id,
    status: bill.status,
    gstin: bill.gstin,
    customerName: bill.customer_name,
    customerPhone: bill.customer_phone,
    subtotalAmount: bill.subtotal_amount,
    taxAmount: bill.tax_amount,
    discountAmount: bill.discount_amount,
    totalAmount: bill.total_amount,
    roundedTotalAmount: bill.rounded_total_amount,
    payments: bill.payments.map((payment) => ({
      id: payment.id,
      billId: payment.bill_id,
      method: payment.method,
      status: payment.status,
      amount: payment.amount,
      referenceNumber: payment.reference_number
    }))
  };
}

export async function listBills(): Promise<Bill[]> {
  const { data } = await apiClient.get<ApiBill[]>("/billing/bills");
  return data.map(mapBill);
}

export async function generateBill(orderId: string): Promise<Bill> {
  const { data } = await apiClient.post<ApiBill>("/billing/generate", { order_id: orderId });
  return mapBill(data);
}

export async function addPayment(
  billId: string,
  payload: { method: PaymentMethod; amount: string; referenceNumber?: string },
): Promise<Bill> {
  const { data } = await apiClient.post<ApiBill>(`/billing/bills/${billId}/payments`, {
    method: payload.method,
    amount: payload.amount,
    reference_number: payload.referenceNumber || null
  });
  return mapBill(data);
}

export async function getReceipt(billId: string): Promise<Receipt> {
  const { data } = await apiClient.get<ApiReceipt>(`/billing/bills/${billId}/receipt`);
  return {
    bill: mapBill(data.bill),
    orderNumber: data.order_number,
    tableId: data.table_id,
    paidAmount: data.paid_amount,
    balanceDue: data.balance_due,
    lines: data.lines.map((line) => ({
      name: line.name,
      quantity: line.quantity,
      unitPrice: line.unit_price,
      taxRate: line.tax_rate,
      lineSubtotal: line.line_subtotal,
      lineTax: line.line_tax,
      lineTotal: line.line_total
    }))
  };
}

