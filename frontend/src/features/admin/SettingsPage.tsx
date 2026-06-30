import { zodResolver } from "@hookform/resolvers/zod";
import { ArrowLeft, Save } from "lucide-react";
import { useForm } from "react-hook-form";
import { Link } from "react-router-dom";
import { z } from "zod";

import { useSettings, useUpsertSetting } from "./hooks";

const settingSchema = z.object({
  key: z.string().min(2),
  value: z.string().min(2),
  isPublic: z.boolean()
});

type SettingForm = z.infer<typeof settingSchema>;

export function SettingsPage() {
  const settings = useSettings();
  const upsertSetting = useUpsertSetting();
  const form = useForm<SettingForm>({
    resolver: zodResolver(settingSchema),
    defaultValues: {
      key: "cafe.profile",
      value: JSON.stringify({ name: "Civet Cafe" }, null, 2),
      isPublic: false
    }
  });

  return (
    <main className="min-h-screen bg-civet-background text-civet-ink">
      <header className="border-b border-civet-outlineVariant bg-civet-surface">
        <div className="mx-auto flex min-h-16 max-w-7xl items-center justify-between px-6">
          <div>
            <p className="text-xs font-semibold uppercase text-civet-muted">Settings</p>
            <h1 className="font-display text-2xl font-semibold">Cafe settings</h1>
          </div>
          <Link aria-label="Back to dashboard" className="grid size-11 place-items-center rounded border border-civet-outlineVariant text-civet-muted" to="/">
            <ArrowLeft aria-hidden="true" size={20} />
          </Link>
        </div>
      </header>

      <section className="mx-auto grid max-w-7xl gap-6 px-6 py-6 lg:grid-cols-[420px_1fr]">
        <form
          className="rounded-lg border border-civet-outlineVariant bg-civet-surface p-4"
          onSubmit={form.handleSubmit(async (values) => {
            await upsertSetting.mutateAsync({
              key: values.key,
              value: JSON.parse(values.value) as Record<string, unknown>,
              isPublic: values.isPublic
            });
          })}
        >
          <h2 className="mb-4 font-display text-xl font-semibold">Edit setting</h2>
          <input {...form.register("key")} aria-label="Setting key" className="mb-3 min-h-12 w-full rounded border border-civet-outlineVariant bg-civet-surfaceLow px-3" />
          <textarea {...form.register("value")} aria-label="Setting value JSON" className="mb-3 min-h-40 w-full rounded border border-civet-outlineVariant bg-civet-surfaceLow p-3 font-mono text-sm" />
          <label className="mb-4 flex min-h-12 items-center gap-3">
            <input {...form.register("isPublic")} type="checkbox" />
            <span className="text-sm font-semibold">Public setting</span>
          </label>
          <button className="flex min-h-12 w-full items-center justify-center gap-2 rounded bg-civet-espresso px-4 text-sm font-semibold text-white" type="submit">
            <Save aria-hidden="true" size={18} />
            Save setting
          </button>
        </form>

        <section className="rounded-lg border border-civet-outlineVariant bg-civet-surface p-4">
          <h2 className="mb-4 font-display text-xl font-semibold">Current settings</h2>
          <div className="grid gap-3">
            {(settings.data ?? []).map((setting) => (
              <article className="rounded border border-civet-outlineVariant bg-civet-surfaceLow p-4" key={setting.id}>
                <div className="mb-2 flex items-center justify-between gap-3">
                  <h3 className="font-semibold">{setting.key}</h3>
                  <span className="text-xs uppercase text-civet-muted">{setting.isPublic ? "public" : "private"}</span>
                </div>
                <pre className="overflow-auto rounded bg-white p-3 text-xs">{JSON.stringify(setting.value, null, 2)}</pre>
              </article>
            ))}
          </div>
        </section>
      </section>
    </main>
  );
}

