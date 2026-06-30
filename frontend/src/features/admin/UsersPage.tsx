import { zodResolver } from "@hookform/resolvers/zod";
import { ArrowLeft, Plus, Trash2 } from "lucide-react";
import { useForm } from "react-hook-form";
import { Link } from "react-router-dom";
import { z } from "zod";

import { useCreateUser, useDeleteUser, useRoles, useUpdateUser, useUsers } from "./hooks";

const userSchema = z.object({
  email: z.string().email(),
  fullName: z.string().min(2),
  roleId: z.string().min(1),
  phone: z.string().optional(),
  employeeCode: z.string().optional(),
  isActive: z.boolean()
});

type UserForm = z.infer<typeof userSchema>;

export function UsersPage() {
  const users = useUsers();
  const roles = useRoles();
  const createUser = useCreateUser();
  const updateUser = useUpdateUser();
  const deleteUser = useDeleteUser();
  const form = useForm<UserForm>({
    resolver: zodResolver(userSchema),
    defaultValues: {
      email: "",
      fullName: "",
      roleId: "",
      phone: "",
      employeeCode: "",
      isActive: true
    }
  });
  const roleById = new Map((roles.data ?? []).map((role) => [role.id, role]));

  return (
    <main className="min-h-screen bg-civet-background text-civet-ink">
      <header className="border-b border-civet-outlineVariant bg-civet-surface">
        <div className="mx-auto flex min-h-16 max-w-7xl items-center justify-between px-6">
          <div>
            <p className="text-xs font-semibold uppercase text-civet-muted">Users</p>
            <h1 className="font-display text-2xl font-semibold">User management</h1>
          </div>
          <Link aria-label="Back to dashboard" className="grid size-11 place-items-center rounded border border-civet-outlineVariant text-civet-muted" to="/">
            <ArrowLeft aria-hidden="true" size={20} />
          </Link>
        </div>
      </header>

      <section className="mx-auto grid max-w-7xl gap-6 px-6 py-6 lg:grid-cols-[360px_1fr]">
        <form
          className="rounded-lg border border-civet-outlineVariant bg-civet-surface p-4"
          onSubmit={form.handleSubmit(async (values) => {
            await createUser.mutateAsync(values);
            form.reset();
          })}
        >
          <h2 className="mb-4 font-display text-xl font-semibold">Add staff</h2>
          <input {...form.register("email")} aria-label="Email" className="mb-3 min-h-12 w-full rounded border border-civet-outlineVariant bg-civet-surfaceLow px-3" placeholder="Email" />
          <input {...form.register("fullName")} aria-label="Full name" className="mb-3 min-h-12 w-full rounded border border-civet-outlineVariant bg-civet-surfaceLow px-3" placeholder="Full name" />
          <select {...form.register("roleId")} aria-label="Role" className="mb-3 min-h-12 w-full rounded border border-civet-outlineVariant bg-civet-surfaceLow px-3">
            <option value="">Select role</option>
            {(roles.data ?? []).map((role) => (
              <option key={role.id} value={role.id}>{role.name}</option>
            ))}
          </select>
          <input {...form.register("phone")} aria-label="Phone" className="mb-3 min-h-12 w-full rounded border border-civet-outlineVariant bg-civet-surfaceLow px-3" placeholder="Phone" />
          <input {...form.register("employeeCode")} aria-label="Employee code" className="mb-4 min-h-12 w-full rounded border border-civet-outlineVariant bg-civet-surfaceLow px-3" placeholder="Employee code" />
          <button className="flex min-h-12 w-full items-center justify-center gap-2 rounded bg-civet-espresso px-4 text-sm font-semibold text-white" type="submit">
            <Plus aria-hidden="true" size={18} />
            Add user
          </button>
        </form>

        <section className="rounded-lg border border-civet-outlineVariant bg-civet-surface p-4">
          <h2 className="mb-4 font-display text-xl font-semibold">Staff list</h2>
          <div className="grid gap-3">
            {(users.data ?? []).map((user) => (
              <article className="flex min-h-16 items-center justify-between gap-3 rounded border border-civet-outlineVariant bg-civet-surfaceLow px-4 py-3" key={user.id}>
                <div>
                  <h3 className="font-semibold">{user.fullName}</h3>
                  <p className="text-sm text-civet-muted">{user.email}</p>
                  <p className="text-xs uppercase text-civet-muted">{roleById.get(user.roleId)?.name ?? "Role"}</p>
                </div>
                <div className="flex gap-2">
                  <button
                    className="min-h-11 rounded border border-civet-outlineVariant px-3 text-sm font-semibold"
                    onClick={() => updateUser.mutate({ id: user.id, payload: { isActive: !user.isActive } })}
                    type="button"
                  >
                    {user.isActive ? "Disable" : "Enable"}
                  </button>
                  <button
                    aria-label={`Delete ${user.fullName}`}
                    className="grid size-11 place-items-center rounded border border-civet-outlineVariant text-civet-terracotta"
                    onClick={() => deleteUser.mutate(user.id)}
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

