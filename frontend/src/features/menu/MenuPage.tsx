import { zodResolver } from "@hookform/resolvers/zod";
import { ArrowLeft, Plus, Trash2 } from "lucide-react";
import { useForm } from "react-hook-form";
import { Link } from "react-router-dom";
import { z } from "zod";

import {
  useCategories,
  useCreateCategory,
  useCreateMenuItem,
  useDeleteCategory,
  useDeleteMenuItem,
  useMenuItems,
  useUpdateCategory,
  useUpdateMenuItem
} from "./hooks";

const categorySchema = z.object({
  name: z.string().min(2),
  description: z.string().optional(),
  displayOrder: z.coerce.number().int().min(0),
  isActive: z.boolean()
});

const itemSchema = z.object({
  categoryId: z.string().min(1),
  sku: z.string().min(2),
  name: z.string().min(2),
  description: z.string().optional(),
  price: z.string().regex(/^\d+(\.\d{1,2})?$/),
  taxRate: z.string().regex(/^\d+(\.\d{1,2})?$/),
  isAvailable: z.boolean(),
  displayOrder: z.coerce.number().int().min(0)
});

type CategoryForm = z.infer<typeof categorySchema>;
type ItemForm = z.infer<typeof itemSchema>;

export function MenuPage() {
  const categories = useCategories();
  const items = useMenuItems();
  const createCategory = useCreateCategory();
  const updateCategory = useUpdateCategory();
  const removeCategory = useDeleteCategory();
  const createItem = useCreateMenuItem();
  const updateItem = useUpdateMenuItem();
  const removeItem = useDeleteMenuItem();

  const categoryForm = useForm<CategoryForm>({
    resolver: zodResolver(categorySchema),
    defaultValues: {
      name: "",
      description: "",
      displayOrder: 0,
      isActive: true
    }
  });

  const itemForm = useForm<ItemForm>({
    resolver: zodResolver(itemSchema),
    defaultValues: {
      categoryId: "",
      sku: "",
      name: "",
      description: "",
      price: "",
      taxRate: "5.00",
      isAvailable: true,
      displayOrder: 0
    }
  });

  const categoryById = new Map((categories.data ?? []).map((category) => [category.id, category]));

  return (
    <main className="min-h-screen bg-civet-background text-civet-ink">
      <header className="border-b border-civet-outlineVariant bg-civet-surface">
        <div className="mx-auto flex min-h-16 max-w-7xl items-center justify-between px-6">
          <div>
            <p className="text-xs font-semibold uppercase text-civet-muted">Menu</p>
            <h1 className="font-display text-2xl font-semibold">Menu management</h1>
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
            onSubmit={categoryForm.handleSubmit(async (values) => {
              await createCategory.mutateAsync(values);
              categoryForm.reset();
            })}
          >
            <h2 className="mb-4 font-display text-xl font-semibold">Categories</h2>
            <input
              {...categoryForm.register("name")}
              aria-label="Category name"
              className="mb-3 min-h-12 w-full rounded border border-civet-outlineVariant bg-civet-surfaceLow px-3 outline-none focus:border-civet-espresso"
              placeholder="Category name"
            />
            <input
              {...categoryForm.register("description")}
              aria-label="Category description"
              className="mb-3 min-h-12 w-full rounded border border-civet-outlineVariant bg-civet-surfaceLow px-3 outline-none focus:border-civet-espresso"
              placeholder="Description"
            />
            <input
              {...categoryForm.register("displayOrder")}
              aria-label="Category order"
              className="mb-3 min-h-12 w-full rounded border border-civet-outlineVariant bg-civet-surfaceLow px-3 outline-none focus:border-civet-espresso"
              min={0}
              type="number"
            />
            <button
              className="flex min-h-12 w-full items-center justify-center gap-2 rounded bg-civet-espresso px-4 text-sm font-semibold text-white"
              disabled={createCategory.isPending}
              type="submit"
            >
              <Plus aria-hidden="true" size={18} />
              Add category
            </button>
          </form>

          <form
            className="rounded-lg border border-civet-outlineVariant bg-civet-surface p-4"
            onSubmit={itemForm.handleSubmit(async (values) => {
              await createItem.mutateAsync(values);
              itemForm.reset();
            })}
          >
            <h2 className="mb-4 font-display text-xl font-semibold">Items</h2>
            <select
              {...itemForm.register("categoryId")}
              aria-label="Item category"
              className="mb-3 min-h-12 w-full rounded border border-civet-outlineVariant bg-civet-surfaceLow px-3 outline-none focus:border-civet-espresso"
            >
              <option value="">Select category</option>
              {(categories.data ?? []).map((category) => (
                <option key={category.id} value={category.id}>
                  {category.name}
                </option>
              ))}
            </select>
            <input
              {...itemForm.register("sku")}
              aria-label="Item SKU"
              className="mb-3 min-h-12 w-full rounded border border-civet-outlineVariant bg-civet-surfaceLow px-3 outline-none focus:border-civet-espresso"
              placeholder="SKU"
            />
            <input
              {...itemForm.register("name")}
              aria-label="Item name"
              className="mb-3 min-h-12 w-full rounded border border-civet-outlineVariant bg-civet-surfaceLow px-3 outline-none focus:border-civet-espresso"
              placeholder="Item name"
            />
            <div className="grid grid-cols-2 gap-3">
              <input
                {...itemForm.register("price")}
                aria-label="Item price"
                className="mb-3 min-h-12 w-full rounded border border-civet-outlineVariant bg-civet-surfaceLow px-3 outline-none focus:border-civet-espresso"
                placeholder="Price"
              />
              <input
                {...itemForm.register("taxRate")}
                aria-label="Item tax rate"
                className="mb-3 min-h-12 w-full rounded border border-civet-outlineVariant bg-civet-surfaceLow px-3 outline-none focus:border-civet-espresso"
                placeholder="GST %"
              />
            </div>
            <button
              className="flex min-h-12 w-full items-center justify-center gap-2 rounded bg-civet-espresso px-4 text-sm font-semibold text-white"
              disabled={createItem.isPending}
              type="submit"
            >
              <Plus aria-hidden="true" size={18} />
              Add item
            </button>
          </form>
        </div>

        <div className="space-y-6">
          <section className="rounded-lg border border-civet-outlineVariant bg-civet-surface p-4">
            <h2 className="mb-4 font-display text-xl font-semibold">Category list</h2>
            <div className="grid gap-3">
              {(categories.data ?? []).map((category) => (
                <article
                  className="flex min-h-16 items-center justify-between rounded border border-civet-outlineVariant bg-civet-surfaceLow px-4"
                  key={category.id}
                >
                  <div>
                    <h3 className="font-semibold">{category.name}</h3>
                    <p className="text-sm text-civet-muted">
                      {category.isActive ? "Active" : "Inactive"}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <button
                      className="min-h-11 rounded border border-civet-outlineVariant px-3 text-sm font-semibold"
                      onClick={() =>
                        updateCategory.mutate({
                          id: category.id,
                          payload: { isActive: !category.isActive }
                        })
                      }
                      type="button"
                    >
                      {category.isActive ? "Disable" : "Enable"}
                    </button>
                    <button
                      aria-label={`Delete ${category.name}`}
                      className="grid size-11 place-items-center rounded border border-civet-outlineVariant text-civet-terracotta"
                      onClick={() => removeCategory.mutate(category.id)}
                      type="button"
                    >
                      <Trash2 aria-hidden="true" size={18} />
                    </button>
                  </div>
                </article>
              ))}
            </div>
          </section>

          <section className="rounded-lg border border-civet-outlineVariant bg-civet-surface p-4">
            <h2 className="mb-4 font-display text-xl font-semibold">Item list</h2>
            <div className="grid gap-3 xl:grid-cols-2">
              {(items.data ?? []).map((item) => (
                <article
                  className="rounded-lg border border-civet-outlineVariant bg-civet-surfaceLow p-4"
                  key={item.id}
                >
                  <div className="mb-4 flex items-start justify-between gap-3">
                    <div>
                      <p className="text-xs font-semibold uppercase text-civet-muted">{item.sku}</p>
                      <h3 className="font-display text-xl font-semibold">{item.name}</h3>
                      <p className="text-sm text-civet-muted">
                        {categoryById.get(item.categoryId)?.name ?? "Uncategorized"}
                      </p>
                    </div>
                    <p className="font-display text-xl font-semibold">INR {item.price}</p>
                  </div>
                  <div className="flex gap-2">
                    <button
                      className="min-h-11 rounded border border-civet-outlineVariant px-3 text-sm font-semibold"
                      onClick={() =>
                        updateItem.mutate({
                          id: item.id,
                          payload: { isAvailable: !item.isAvailable }
                        })
                      }
                      type="button"
                    >
                      {item.isAvailable ? "Mark unavailable" : "Mark available"}
                    </button>
                    <button
                      aria-label={`Delete ${item.name}`}
                      className="grid size-11 place-items-center rounded border border-civet-outlineVariant text-civet-terracotta"
                      onClick={() => removeItem.mutate(item.id)}
                      type="button"
                    >
                      <Trash2 aria-hidden="true" size={18} />
                    </button>
                  </div>
                </article>
              ))}
            </div>
          </section>
        </div>
      </section>
    </main>
  );
}
