import { zodResolver } from "@hookform/resolvers/zod";
import { ArrowLeft, Plus, Trash2 } from "lucide-react";
import { useForm } from "react-hook-form";
import { Link } from "react-router-dom";
import { z } from "zod";

import { useCreateTable, useDeleteTable, useFloors, useTables, useUpdateTable } from "./hooks";
import type { TableStatus } from "./types";

const tableSchema = z.object({
  tableNumber: z.string().min(1),
  floor: z.string().min(1),
  capacity: z.coerce.number().int().min(1).max(50),
  status: z.enum(["available", "occupied", "reserved", "inactive"])
});

type TableForm = z.infer<typeof tableSchema>;

const statusOptions: TableStatus[] = ["available", "occupied", "reserved", "inactive"];

const statusClass: Record<TableStatus, string> = {
  available: "bg-green-50 text-green-700 border-green-200",
  occupied: "bg-red-50 text-red-700 border-red-200",
  reserved: "bg-yellow-50 text-yellow-800 border-yellow-200",
  inactive: "bg-zinc-100 text-zinc-600 border-zinc-200"
};

export function TablesPage() {
  const tables = useTables();
  const floors = useFloors();
  const createTable = useCreateTable();
  const updateTable = useUpdateTable();
  const removeTable = useDeleteTable();
  const form = useForm<TableForm>({
    resolver: zodResolver(tableSchema),
    defaultValues: {
      tableNumber: "",
      floor: "Main",
      capacity: 2,
      status: "available"
    }
  });

  return (
    <main className="min-h-screen bg-civet-background text-civet-ink">
      <header className="border-b border-civet-outlineVariant bg-civet-surface">
        <div className="mx-auto flex min-h-16 max-w-7xl items-center justify-between px-6">
          <div>
            <p className="text-xs font-semibold uppercase text-civet-muted">Tables</p>
            <h1 className="font-display text-2xl font-semibold">Floor management</h1>
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

      <section className="mx-auto grid max-w-7xl gap-6 px-6 py-6 lg:grid-cols-[340px_1fr]">
        <div className="space-y-6">
          <form
            className="rounded-lg border border-civet-outlineVariant bg-civet-surface p-4"
            onSubmit={form.handleSubmit(async (values) => {
              await createTable.mutateAsync(values);
              form.reset();
            })}
          >
            <h2 className="mb-4 font-display text-xl font-semibold">Add table</h2>
            <input
              {...form.register("tableNumber")}
              aria-label="Table number"
              className="mb-3 min-h-12 w-full rounded border border-civet-outlineVariant bg-civet-surfaceLow px-3 outline-none focus:border-civet-espresso"
              placeholder="Table number"
            />
            <input
              {...form.register("floor")}
              aria-label="Floor"
              className="mb-3 min-h-12 w-full rounded border border-civet-outlineVariant bg-civet-surfaceLow px-3 outline-none focus:border-civet-espresso"
              placeholder="Floor"
            />
            <input
              {...form.register("capacity")}
              aria-label="Capacity"
              className="mb-3 min-h-12 w-full rounded border border-civet-outlineVariant bg-civet-surfaceLow px-3 outline-none focus:border-civet-espresso"
              min={1}
              type="number"
            />
            <select
              {...form.register("status")}
              aria-label="Status"
              className="mb-4 min-h-12 w-full rounded border border-civet-outlineVariant bg-civet-surfaceLow px-3 outline-none focus:border-civet-espresso"
            >
              {statusOptions.map((status) => (
                <option key={status} value={status}>
                  {status}
                </option>
              ))}
            </select>
            <button
              className="flex min-h-12 w-full items-center justify-center gap-2 rounded bg-civet-espresso px-4 text-sm font-semibold text-white"
              disabled={createTable.isPending}
              type="submit"
            >
              <Plus aria-hidden="true" size={18} />
              Add table
            </button>
          </form>

          <section className="rounded-lg border border-civet-outlineVariant bg-civet-surface p-4">
            <h2 className="mb-4 font-display text-xl font-semibold">Floors</h2>
            <div className="space-y-3">
              {(floors.data ?? []).map((floor) => (
                <article className="rounded border border-civet-outlineVariant bg-civet-surfaceLow p-3" key={floor.floor}>
                  <div className="flex items-center justify-between">
                    <h3 className="font-semibold">{floor.floor}</h3>
                    <span className="text-sm text-civet-muted">{floor.tableCount} tables</span>
                  </div>
                  <p className="mt-1 text-sm text-civet-muted">
                    {floor.availableCount} available · {floor.occupiedCount} occupied · {floor.reservedCount} reserved
                  </p>
                </article>
              ))}
            </div>
          </section>
        </div>

        <section className="rounded-lg border border-civet-outlineVariant bg-civet-surface p-4">
          <h2 className="mb-4 font-display text-xl font-semibold">Table list</h2>
          <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
            {(tables.data ?? []).map((table) => (
              <article className="rounded-lg border border-civet-outlineVariant bg-civet-surfaceLow p-4" key={table.id}>
                <div className="mb-4 flex items-start justify-between">
                  <div>
                    <p className="text-xs font-semibold uppercase text-civet-muted">{table.floor}</p>
                    <h3 className="font-display text-2xl font-semibold">Table {table.tableNumber}</h3>
                    <p className="text-sm text-civet-muted">{table.capacity} seats</p>
                  </div>
                  <span className={`rounded-full border px-3 py-1 text-xs font-semibold ${statusClass[table.status]}`}>
                    {table.status}
                  </span>
                </div>
                <div className="flex gap-2">
                  <select
                    aria-label={`Status for table ${table.tableNumber}`}
                    className="min-h-11 flex-1 rounded border border-civet-outlineVariant bg-civet-surface px-3 text-sm"
                    onChange={(event) =>
                      updateTable.mutate({
                        id: table.id,
                        payload: { status: event.target.value as TableStatus }
                      })
                    }
                    value={table.status}
                  >
                    {statusOptions.map((status) => (
                      <option key={status} value={status}>
                        {status}
                      </option>
                    ))}
                  </select>
                  <button
                    aria-label={`Delete table ${table.tableNumber}`}
                    className="grid size-11 place-items-center rounded border border-civet-outlineVariant text-civet-terracotta disabled:opacity-40"
                    disabled={table.status === "occupied"}
                    onClick={() => removeTable.mutate(table.id)}
                    type="button"
                  >
                    <Trash2 aria-hidden="true" size={18} />
                  </button>
                </div>
              </article>
            ))}
          </div>
        </section>
      </section>
    </main>
  );
}

