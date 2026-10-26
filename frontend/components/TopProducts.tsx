"use client";

import { motion } from "motion/react";
import { usePolling } from "@/lib/usePolling";

type Top = { product_id: number; name: string; image_url: string | null; units: number };

export default function TopProducts() {
  const { data, error } = usePolling<Top[]>("/sales/top-products?days=30&limit=5", 5000);
  const list = data ?? [];
  const max = Math.max(1, ...list.map((p) => p.units));

  return (
    <motion.section
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.45 }}
      className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200"
    >
      <h2 className="text-lg font-semibold">Top 5 products</h2>
      <p className="mb-5 text-xs text-slate-500">Units sold, last 30 days</p>

      {error && !data && <p className="text-sm text-red-600">{error}</p>}
      {data && list.length === 0 && <p className="text-sm text-slate-500">No sales in the last 30 days.</p>}

      <ol className="space-y-4">
        {list.map((p, i) => (
          // layout: when the ranking changes, rows glide to their new place
          <motion.li
            key={p.product_id}
            layout
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
          >
            <div className="mb-1 flex items-center justify-between text-sm">
              <span className="flex items-center gap-2 font-medium">
                <span className="flex size-6 items-center justify-center rounded-full bg-indigo-50 text-xs text-indigo-700">
                  {i + 1}
                </span>
                {p.name}
              </span>
              <span className="tabular-nums text-slate-600">{p.units}</span>
            </div>
            <div className="h-1.5 rounded-full bg-slate-100">
              <motion.div
                className="h-1.5 rounded-full bg-indigo-500"
                initial={{ width: 0 }}
                animate={{ width: `${(p.units / max) * 100}%` }}
                transition={{ duration: 0.6 }}
              />
            </div>
          </motion.li>
        ))}
      </ol>
    </motion.section>
  );
}