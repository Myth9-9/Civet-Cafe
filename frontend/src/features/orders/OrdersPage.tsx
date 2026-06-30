import { zodResolver } from "@hookform/resolvers/zod";
import { ArrowLeft, Plus } from "lucide-react";
import { useForm } from "react-hook-form";
import { Link } from "react-router-dom";
import { z } from "zod";

import { useMenuItems } from "../menu/hooks";
import { useTables } from "../tables/hooks";
import { useAddOrderItem, useCreateOrder, useOrders, useTransitionOrder } from "./hooks";
import type { OrderStatus } from "./types";

const orderSchema = z.object({
  tableId: z.string().optional(),
  notes: z.string().optional()
});

const itemSchema = z.object({
  orderId: z.string().min(1),
  menuItemId: z.string().min(1),
  quantity: z.coerce.number().int().min(1).max(100)
});

type OrderForm = z.infer<typeof orderSchema>;
type ItemForm = z.infer<typeof itemSchema>;

const nextStatuses: Record<OrderStatus, OrderStatus[]> = {
  draft: ["placed", "cancelled"],
  placed: ["preparing", "cancelled"],
  preparing: ["ready", "cancelled"],
  ready: ["served", "cancelled"],
  served: ["billed"],
  cancelled: [],
  billed: []
};

export function OrdersPage() {
  const orders = useOrders();
  const tables = useTables();
  const menuItems = useMenuItems();
  const createOrder = useCreateOrder();
  const addItem = useAddOrderItem();
  const transition = useTransitionOrder();

  const orderForm = useForm<OrderForm>({
    resolver: zodResolver(orderSchema),
    defaultValues: { tableId: "", notes: "" }
  });
  const itemForm = useForm<ItemForm>({
    resolver: zodResolver(itemSchema),
    defaultValues: { orderId: "", menuItemId: "", quantity: 1 }
  });

  const tableById = new Map((tables.data ?? []).map((table) => [table.id, table]));

  return (
    <main className="min-h-screen bg-civet-background text-civet-ink">
      <header className="border-b border-civet-outlineVariant bg-civet-surface">
        <div className="mx-auto flex min-h-16 max-w-7xl items-center justify-between px-6">
          <div>
            <p className="text-xs font-semibold uppercase text-civet-muted">Orders</p>
            <h1 className="font-display text-2xl font-semibold">Order management</h1>
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
          <form
            className="rounded-lg border border-civet-outlineVariant bg-civet-surface p-4"
            onSubmit={orderForm.handleSubmit(async (values) => {
              await createOrder.mutateAsync(values);
              orderForm.reset();
            })}
          >
            <h2 className="mb-4 font-display text-xl font-semibold">New order</h2>
            <select
              {...orderForm.register("tableId")}
              aria-label="Order table"
              className="mb-3 min-h-12 w-full rounded border border-civet-outlineVariant bg-civet-surfaceLow px-3 outline-none focus:border-civet-espresso"
            >
              <option value="">Takeaway / no table</option>
              {(tables.data ?? []).map((table) => (
                <option key={table.id} value={table.id}>
                  {table.floor} - Table {table.tableNumber}
                </option>
              ))}
            </select>
            <input
              {...orderForm.register("notes")}
              aria-label="Order notes"
              className="mb-3 min-h-12 w-full rounded border border-civet-outlineVariant bg-civet-surfaceLow px-3 outline-none focus:border-civet-espresso"
              placeholder="Notes"
            />
            <button className="flex min-h-12 w-full items-center justify-center gap-2 rounded bg-civet-espresso px-4 text-sm font-semibold text-white" type="submit">
              <Plus aria-hidden="true" size={18} />
              Create draft
            </button>
          </form>

          <form
            className="rounded-lg border border-civet-outlineVariant bg-civet-surface p-4"
            onSubmit={itemForm.handleSubmit(async (values) => {
              await addItem.mutateAsync({
                orderId: values.orderId,
                payload: {
                  menuItemId: values.menuItemId,
                  quantity: values.quantity
                }
              });
              itemForm.reset();
            })}
          >
            <h2 className="mb-4 font-display text-xl font-semibold">Add item</h2>
            <select
              {...itemForm.register("orderId")}
              aria-label="Target order"
              className="mb-3 min-h-12 w-full rounded border border-civet-outlineVariant bg-civet-surfaceLow px-3 outline-none focus:border-civet-espresso"
            >
              <option value="">Select order</option>
              {(orders.data ?? [])
                .filter((order) => order.status === "draft" || order.status === "placed")
                .map((order) => (
                  <option key={order.id} value={order.id}>
                    {order.orderNumber}
                  </option>
                ))}
            </select>
            <select
              {...itemForm.register("menuItemId")}
              aria-label="Menu item"
              className="mb-3 min-h-12 w-full rounded border border-civet-outlineVariant bg-civet-surfaceLow px-3 outline-none focus:border-civet-espresso"
            >
              <option value="">Select item</option>
              {(menuItems.data ?? []).map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name} - INR {item.price}
                </option>
              ))}
            </select>
            <input
              {...itemForm.register("quantity")}
              aria-label="Quantity"
              className="mb-3 min-h-12 w-full rounded border border-civet-outlineVariant bg-civet-surfaceLow px-3 outline-none focus:border-civet-espresso"
              min={1}
              type="number"
            />
            <button className="flex min-h-12 w-full items-center justify-center gap-2 rounded bg-civet-espresso px-4 text-sm font-semibold text-white" type="submit">
              <Plus aria-hidden="true" size={18} />
              Add to order
            </button>
          </form>
        </div>

        <section className="rounded-lg border border-civet-outlineVariant bg-civet-surface p-4">
          <h2 className="mb-4 font-display text-xl font-semibold">Active orders</h2>
          <div className="grid gap-4">
            {(orders.data ?? []).map((order) => (
              <article className="rounded-lg border border-civet-outlineVariant bg-civet-surfaceLow p-4" key={order.id}>
                <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <p className="text-xs font-semibold uppercase text-civet-muted">{order.orderNumber}</p>
                    <h3 className="font-display text-xl font-semibold">
                      {order.tableId ? `Table ${tableById.get(order.tableId)?.tableNumber ?? ""}` : "Takeaway"}
                    </h3>
                    <p className="text-sm text-civet-muted">{order.status}</p>
                  </div>
                  <p className="font-display text-2xl font-semibold">INR {order.totalAmount}</p>
                </div>
                <div className="mb-4 divide-y divide-civet-outlineVariant">
                  {order.items.map((item) => (
                    <div className="flex min-h-11 items-center justify-between gap-3 py-2" key={item.id}>
                      <span>{item.quantity} x {item.itemNameSnapshot}</span>
                      <span className="font-semibold">INR {item.lineTotal}</span>
                    </div>
                  ))}
                </div>
                <div className="flex flex-wrap gap-2">
                  {nextStatuses[order.status].map((status) => (
                    <button
                      className="min-h-11 rounded border border-civet-outlineVariant px-3 text-sm font-semibold"
                      key={status}
                      onClick={() => transition.mutate({ orderId: order.id, status })}
                      type="button"
                    >
                      Mark {status}
                    </button>
                  ))}
                </div>
              </article>
            ))}
          </div>
        </section>
      </section>
    </main>
  );
}

