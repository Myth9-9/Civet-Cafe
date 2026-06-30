import { apiClient } from "../../lib/apiClient";
import type { SalesReport } from "./types";

type ApiSalesReport = {
  period_start: string;
  period_end: string;
  bill_count: number;
  paid_bill_count: number;
  gross_sales: string;
  net_sales: string;
  tax_collected: string;
  discounts: string;
  payments_collected: string;
  average_bill_value: string;
  payment_methods: { method: string; amount: string }[];
};

function mapReport(report: ApiSalesReport): SalesReport {
  return {
    periodStart: report.period_start,
    periodEnd: report.period_end,
    billCount: report.bill_count,
    paidBillCount: report.paid_bill_count,
    grossSales: report.gross_sales,
    netSales: report.net_sales,
    taxCollected: report.tax_collected,
    discounts: report.discounts,
    paymentsCollected: report.payments_collected,
    averageBillValue: report.average_bill_value,
    paymentMethods: report.payment_methods.map((method) => ({
      method: method.method,
      amount: method.amount
    }))
  };
}

export async function getDailyReport(reportDate: string): Promise<SalesReport> {
  const { data } = await apiClient.get<ApiSalesReport>("/reports/daily", {
    params: { report_date: reportDate }
  });
  return mapReport(data);
}

export async function getMonthlyReport(year: number, month: number): Promise<SalesReport> {
  const { data } = await apiClient.get<ApiSalesReport>("/reports/monthly", {
    params: { year, month }
  });
  return mapReport(data);
}

