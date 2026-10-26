"use client";

import { useState } from "react";
import type { ChangeEvent, FormEvent, ReactNode } from "react";
import { AnimatePresence, motion } from "motion/react";
import { post, Category } from "@/lib/api";

type Props = {
  open: boolean;
  categories: Category[];
  onClose: () => void;
  onCreated: () => void;
};

const EMPTY = {
  name: "",
  sku: "",
  category_id: "",
  unit_price: "",
  initial_stock: "0",
  reorder_level: "10",
  image_url: "",
};

const input =
  "w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500";

function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <label className="block text-sm">
      <span className="mb-1 block font-medium text-slate-700">{label}</span>
      {children}
    </label>
  );
}

export default function AddProductDialog({ open, categories, onClose, onCreated }: Props) {
  const [form, setForm] = useState(EMPTY);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // one handler for every field: update just that key of the form
  const set =
    (key: keyof typeof EMPTY) => (e: ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
      setForm({ ...form, [key]: e.target.value });

  async function submit(e: FormEvent) {
    e.preventDefault();
    setError(null);

    const price = Number(form.unit_price);
    if (!form.name.trim() || !form.sku.trim()) return setError("Name and SKU are required");
    if (!form.category_id) return setError("Please choose a category");
    if (!(price > 0)) return setError("Price must be more than 0");

    setSaving(true);
    try {
      await post("/products/", {
        name: form.name.trim(),
        sku: form.sku.trim(),
        category_id: Number(form.category_id),
        unit_price: price,
        reorder_level: Number(form.reorder_level) || 0,
        initial_stock: Number(form.initial_stock) || 0,
        image_url: form.image_url.trim() || null,
      });
      setForm(EMPTY);
      onCreated();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          key="overlay"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
          className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4"
        >
          <motion.form
            initial={{ opacity: 0, y: 24, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 24 }}
            onClick={(e) => e.stopPropagation()}
            onSubmit={submit}
            className="max-h-[90vh] w-full max-w-lg space-y-4 overflow-y-auto rounded-2xl bg-white p-6 shadow-xl"
          >
            <h2 className="text-xl font-semibold">Add product</h2>

            <Field label="Product name">
              <input className={input} value={form.name} onChange={set("name")} placeholder="e.g. Wireless Mouse" />
            </Field>

            <div className="grid grid-cols-2 gap-4">
              <Field label="SKU">
                <input className={input} value={form.sku} onChange={set("sku")} placeholder="e.g. SKU2001" />
              </Field>
              <Field label="Category">
                <select className={input} value={form.category_id} onChange={set("category_id")}>
                  <option value="">Choose...</option>
                  {categories.map((c) => (
                    <option key={c.id} value={c.id}>{c.name}</option>
                  ))}
                </select>
              </Field>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <Field label="Price (₹)">
                <input className={input} type="number" min="0" step="0.01" value={form.unit_price} onChange={set("unit_price")} />
              </Field>
              <Field label="Units in stock">
                <input className={input} type="number" min="0" step="1" value={form.initial_stock} onChange={set("initial_stock")} />
              </Field>
              <Field label="Reorder level">
                <input className={input} type="number" min="0" step="1" value={form.reorder_level} onChange={set("reorder_level")} />
              </Field>
            </div>

            <Field label="Photo link (optional)">
              <input className={input} value={form.image_url} onChange={set("image_url")} placeholder="https://.../photo.jpg" />
            </Field>
            {form.image_url.trim() && (
              // eslint-disable-next-line @next/next/no-img-element
              <img src={form.image_url.trim()} alt="Preview" className="h-32 w-full rounded-lg object-cover ring-1 ring-slate-200" />
            )}

            {error && <p className="rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</p>}

            <div className="flex justify-end gap-3 pt-2">
              <button type="button" onClick={onClose} className="rounded-lg px-4 py-2 text-sm text-slate-600 hover:bg-slate-100">
                Cancel
              </button>
              <button
                type="submit"
                disabled={saving}
                className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500 disabled:opacity-50"
              >
                {saving ? "Saving..." : "Save product"}
              </button>
            </div>
          </motion.form>
        </motion.div>
      )}
    </AnimatePresence>
  );
}