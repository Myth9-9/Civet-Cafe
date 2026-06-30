import { zodResolver } from "@hookform/resolvers/zod";
import { AxiosError } from "axios";
import { Coffee, LockKeyhole, Mail } from "lucide-react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { useAuth } from "./useAuth";

const loginSchema = z.object({
  email: z.string().email("Enter a valid staff email"),
  password: z.string().min(8, "Password must be at least 8 characters")
});

type LoginFormValues = z.infer<typeof loginSchema>;

function authErrorMessage(error: unknown): string {
  if (error instanceof AxiosError && error.response?.status === 401) {
    return "Invalid email or password";
  }
  if (error instanceof AxiosError && error.response?.status === 403) {
    return "This staff account is not provisioned for POS access";
  }
  return "Unable to sign in right now";
}

export function LoginPage() {
  const { login, isLoggingIn } = useAuth();
  const {
    register,
    handleSubmit,
    formState: { errors },
    setError
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: "",
      password: ""
    }
  });

  const onSubmit = handleSubmit(async (values) => {
    try {
      await login(values);
    } catch (error) {
      setError("root", { message: authErrorMessage(error) });
    }
  });

  return (
    <main className="min-h-screen bg-civet-background text-civet-ink">
      <section className="mx-auto grid min-h-screen w-full max-w-6xl items-center gap-10 px-6 py-8 lg:grid-cols-[1fr_420px]">
        <div className="max-w-2xl">
          <div className="mb-8 flex items-center gap-3">
            <span className="grid size-12 place-items-center rounded bg-civet-espresso text-white shadow-[0_8px_24px_rgba(62,39,35,0.12)]">
              <Coffee aria-hidden="true" size={26} />
            </span>
            <div>
              <p className="font-sans text-xs font-semibold uppercase text-civet-muted">
                Civet Cafe
              </p>
              <h1 className="font-display text-4xl font-semibold leading-tight">
                POS & Billing System
              </h1>
            </div>
          </div>
          <p className="max-w-xl text-lg leading-7 text-civet-muted">
            Secure staff access for table service, billing, menu management, and daily cafe
            operations.
          </p>
        </div>

        <form
          onSubmit={onSubmit}
          className="rounded-lg border border-civet-outlineVariant bg-civet-surface p-6 shadow-[0_12px_32px_rgba(62,39,35,0.08)]"
        >
          <div className="mb-6">
            <p className="font-sans text-xs font-semibold uppercase text-civet-muted">
              Staff Login
            </p>
            <h2 className="font-display text-2xl font-semibold">Open register</h2>
          </div>

          <label className="mb-4 block">
            <span className="mb-2 block text-sm font-semibold">Email</span>
            <span className="flex min-h-12 items-center gap-3 rounded border border-civet-outlineVariant bg-civet-surfaceLow px-3 focus-within:border-civet-espresso">
              <Mail aria-hidden="true" className="text-civet-muted" size={20} />
              <input
                {...register("email")}
                autoComplete="email"
                className="min-h-12 w-full bg-transparent text-base outline-none"
                type="email"
              />
            </span>
            {errors.email && <span className="mt-1 block text-sm text-civet-terracotta">{errors.email.message}</span>}
          </label>

          <label className="mb-5 block">
            <span className="mb-2 block text-sm font-semibold">Password</span>
            <span className="flex min-h-12 items-center gap-3 rounded border border-civet-outlineVariant bg-civet-surfaceLow px-3 focus-within:border-civet-espresso">
              <LockKeyhole aria-hidden="true" className="text-civet-muted" size={20} />
              <input
                {...register("password")}
                autoComplete="current-password"
                className="min-h-12 w-full bg-transparent text-base outline-none"
                type="password"
              />
            </span>
            {errors.password && (
              <span className="mt-1 block text-sm text-civet-terracotta">{errors.password.message}</span>
            )}
          </label>

          {errors.root && (
            <div className="mb-4 rounded bg-red-50 px-3 py-2 text-sm text-civet-terracotta">
              {errors.root.message}
            </div>
          )}

          <button
            className="min-h-12 w-full rounded bg-civet-espresso px-4 text-sm font-semibold text-white shadow-inner disabled:cursor-not-allowed disabled:opacity-70"
            disabled={isLoggingIn}
            type="submit"
          >
            {isLoggingIn ? "Signing in" : "Sign in"}
          </button>
        </form>
      </section>
    </main>
  );
}
