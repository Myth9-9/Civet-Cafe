export type PaymentMethodTotal = {
  method: string;
  amount: string;
};

export type SalesReport = {
  periodStart: string;
  periodEnd: string;
  billCount: number;
  paidBillCount: number;
  grossSales: string;
  netSales: string;
  taxCollected: string;
  discounts: string;
  paymentsCollected: string;
  averageBillValue: string;
  paymentMethods: PaymentMethodTotal[];
};

