import { zodResolver } from "@hookform/resolvers/zod";
import { ArrowLeft, Printer } from "lucide-react";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { Link } from "react-router-dom";
import { z } from "zod";

import { useOrders } from "../orders/hooks";
import { useAddPayment, useBills, useGenerateBill, useReceipt } from "./hooks";
import type { PaymentMethod } from "./types";

const paymentSchema = z.object({
  billId: z.string().min(1),
  method: z.enum(["cash", "card", "upi", "wallet", "mixed"]),
  amount: z.string().regex(/^\d+(\.\d{1,2})?$/),
  referenceNumber: z.string().optional()
});

type PaymentForm = z.infer<typeof paymentSchema>;

const paymentMethods: PaymentMethod[] = ["cash", "card", "upi", "wallet", "mixed"];

export function BillingPage() {
  const [receiptBillId, setReceiptBillId] = useState<string | null>(null);
  const bills = useBills();
  const orders = useOrders();
  const receipt = useReceipt(receiptBillId);
  const generateBill = useGenerateBill();
  const addPayment = useAddPayment();
  const paymentForm = useForm<PaymentForm>({
    resolver: zodResolver(paymentSchema),
    defaultValues: {
      billId: "",
      method: "cash",
      amount: "",
      referenceNumber: ""
    }
  });

  const servedOrders = (orders.data ?? []).filter((order) => order.status === "served");

  return (
    <main className="min-h-screen bg-civet-background text-civet-ink">
      <header className="border-b border-civet-outlineVariant bg-civet-surface">
        <div className="mx-auto flex min-h-16 max-w-7xl items-center justify-between px-6">
          <div>
            <p className="text-xs font-semibold uppercase text-civet-muted">Billing</p>
            <h1 className="font-display text-2xl font-semibold">Bills & receipts</h1>
          </div>
          <Link
            aria-label="Back to dashboard"
            className="grid size-11 place-items-center rounded border border-civet-outlineVariant text-civet-muted"
            to="/"
          >
            <ArrowLeft aria-hidden="true" size={20} />
          </Link>
        </div>
      </header>

      <section className="mx-auto grid max-w-7xl gap-6 px-6 py-6 lg:grid-cols-[360px_1fr]">
        <div className="space-y-6">
          <section className="rounded-lg border border-civet-outlineVariant bg-civet-surface p-4">
            <h2 className="mb-4 font-display text-xl font-semibold">Generate bill</h2>
            <div className="space-y-3">
              {servedOrders.map((order) => (
                <button
                  className="flex min-h-12 w-full items-center justify-between rounded border border-civet-outlineVariant bg-civet-surfaceLow px-3 text-left"
                  key={order.id}
                  onClick={() => generateBill.mutate(order.id)}
                  type="button"
                >
                  <span>{order.orderNumber}</span>
                  <span className="font-semibold">INR {order.totalAmount}</span>
                </button>
              ))}
              {servedOrders.length === 0 && <p className="text-sm text-civet-muted">No served orders ready for billing.</p>}
            </div>
          </section>

          <form
            className="rounded-lg border border-civet-outlineVariant bg-civet-surface p-4"
            onSubmit={paymentForm.handleSubmit(async (values) => {
              await addPayment.mutateAsync({
                billId: values.billId,
                payload: {
                  method: values.method,
                  amount: values.amount,
                  referenceNumber: values.referenceNumber
                }
              });
              paymentForm.reset();
            })}
          >
            <h2 className="mb-4 font-display text-xl font-semibold">Record payment</h2>
            <select
              {...paymentForm.register("billId")}
              aria-label="Bill"
              className="mb-3 min-h-12 w-full rounded border border-civet-outlineVariant bg-civet-surfaceLow px-3 outline-none focus:border-civet-espresso"
            >
              <option value="">Select bill</option>
              {(bills.data ?? [])
                .filter((bill) => bill.status === "issued")
                .map((bill) => (
                  <option key={bill.id} value={bill.id}>
                    {bill.billNumber} - INR {bill.roundedTotalAmount}
                  </option>
                ))}
            </select>
            <select
              {...paymentForm.register("method")}
              aria-label="Payment method"
              className="mb-3 min-h-12 w-full rounded border border-civet-outlineVariant bg-civet-surfaceLow px-3 outline-none focus:border-civet-espresso"
            >
              {paymentMethods.map((method) => (
                <option key={method} value={method}>
                  {method}
                </option>
              ))}
            </select>
            <input
              {...paymentForm.register("amount")}
              aria-label="Payment amount"
              className="mb-3 min-h-12 w-full rounded border border-civet-outlineVariant bg-civet-surfaceLow px-3 outline-none focus:border-civet-espresso"
              placeholder="Amount"
            />
            <input
              {...paymentForm.register("referenceNumber")}
              aria-label="Reference number"
              className="mb-4 min-h-12 w-full rounded border border-civet-outlineVariant bg-civet-surfaceLow px-3 outline-none focus:border-civet-espresso"
              placeholder="Reference number"
            />
            <button className="min-h-12 w-full rounded bg-civet-espresso px-4 text-sm font-semibold text-white" type="submit">
              Save payment
            </button>
          </form>
        </div>

        <div className="space-y-6">
          <section className="rounded-lg border border-civet-outlineVariant bg-civet-surface p-4">
            <h2 className="mb-4 font-display text-xl font-semibold">Bills</h2>
            <div className="grid gap-3">
              {(bills.data ?? []).map((bill) => (
                <article className="rounded-lg border border-civet-outlineVariant bg-civet-surfaceLow p-4" key={bill.id}>
                  <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <p className="text-xs font-semibold uppercase text-civet-muted">{bill.billNumber}</p>
                      <h3 className="font-display text-xl font-semibold">INR {bill.roundedTotalAmount}</h3>
                      <p className="text-sm text-civet-muted">{bill.status}</p>
                    </div>
                    <button
                      className="inline-flex min-h-11 items-center gap-2 rounded border border-civet-outlineVariant px-3 text-sm font-semibold"
                      onClick={() => setReceiptBillId(bill.id)}
                      type="button"
                    >
                      <Printer aria-hidden="true" size={18} />
                      Receipt
                    </button>
                  </div>
                  <p className="text-sm text-civet-muted">
                    Paid INR {bill.payments.reduce((sum, payment) => sum + Number(payment.amount), 0).toFixed(2)}
                  </p>
                </article>
              ))}
            </div>
          </section>

          {receipt.data && (
            <section className="rounded-lg border border-civet-outlineVariant bg-white p-5 text-civet-ink print:rounded-none print:border-0">
              <div className="mb-4 text-center">
                <h2 className="font-display text-2xl font-semibold">Civet Cafe</h2>
                <p className="text-sm text-civet-muted">GST Bill</p>
                <p className="text-sm text-civet-muted">{receipt.data.bill.billNumber}</p>
              </div>
              <div className="mb-4 divide-y divide-civet-outlineVariant">
                {receipt.data.lines.map((line) => (
                  <div className="flex justify-between gap-3 py-2" key={`${line.name}-${line.quantity}`}>
                    <span>{line.quantity} x {line.name}</span>
                    <span>INR {line.lineTotal}</span>
                  </div>
                ))}
              </div>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between"><span>Subtotal</span><span>INR {receipt.data.bill.subtotalAmount}</span></div>
                <div className="flex justify-between"><span>GST</span><span>INR {receipt.data.bill.taxAmount}</span></div>
                <div className="flex justify-between font-semibold"><span>Total</span><span>INR {receipt.data.bill.roundedTotalAmount}</span></div>
                <div className="flex justify-between"><span>Paid</span><span>INR {receipt.data.paidAmount}</span></div>
                <div className="flex justify-between"><span>Balance</span><span>INR {receipt.data.balanceDue}</span></div>
              </div>
              <button
                className="mt-5 min-h-11 w-full rounded bg-civet-espresso px-4 text-sm font-semibold text-white print:hidden"
                onClick={() => window.print()}
                type="button"
              >
                Print receipt
              </button>
            </section>
          )}
        </div>
      </section>
    </main>
  );
}

