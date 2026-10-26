"use client";

import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import { usePolling } from "@/lib/usePolling";

type Row = {
  product_id: number;
  name: string;
  category_name: string | null;
  current_stock: number;
  reorder_level: number;
  predicted_demand: number | null;
  suggested_order_qty: number;
  source: "forecast" | "rule";
};

type Props = { open: boolean; onClose: () => void };

export default function LowStockDialog({ open, onClose }: Props) {
  return <AnimatePresence>{open && <Panel key="low-stock" onClose={onClose} />}</AnimatePresence>;
}

// The panel only exists while the dialog is open, so the data is fetched
// (and refreshed every 10 seconds) only while someone is looking at it.
function Panel({ onClose }: { onClose: () => void }) {
  const [horizon, setHorizon] = useState(7);
  const { data, error } = usePolling<Row[]>(`/inventory/reorder-plan?horizon=${horizon}`, 10000);
  const rows = data ?? [];
  const totalToOrder = rows.reduce((sum, r) => sum + r.suggested_order_qty, 0);

  // Esc closes the dialog
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  const toggle = (active: boolean) =>
    `rounded-lg px-3 py-1.5 text-sm font-medium transition ${
      active ? "bg-indigo-600 text-white" : "bg-slate-100 text-slate-600 hover:bg-slate-200"
    }`;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={onClose}
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4"
    >
      <motion.div
        initial={{ opacity: 0, y: 32, scale: 0.96 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: 32, scale: 0.96 }}
        transition={{ type: "spring", stiffness: 260, damping: 26 }}
        onClick={(e) => e.stopPropagation()}
        className="max-h-[90vh] w-full max-w-5xl overflow-y-auto rounded-3xl bg-white p-8 shadow-2xl"
      >
        <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
          <div>
            <h2 className="text-2xl font-bold">⚠️ Low stock — reorder plan</h2>
            <p className="text-sm text-slate-500">
              Products at or below their reorder level, and how many to order.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button className={toggle(horizon === 7)} onClick={() => setHorizon(7)}>7 days</button>
            <button className={toggle(horizon === 30)} onClick={() => setHorizon(30)}>30 days</button>
            <button
              onClick={onClose}
              aria-label="Close"
              className="ml-2 flex size-9 items-center justify-center rounded-lg text-slate-500 hover:bg-slate-100"
            >
              ✕
            </button>
          </div>
        </div>

        {error && !data && <p className="text-red-600">{error}</p>}
        {!data && !error && <p className="text-slate-500">Calculating forecasts...</p>}
        {data && rows.length === 0 && (
          <p className="rounded-xl bg-emerald-50 p-6 text-center text-emerald-700">
            All products have enough stock right now 🎉
          </p>
        )}

        {rows.length > 0 && (
          <>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="text-xs uppercase tracking-wide text-slate-500">
                  <tr className="border-b border-slate-200">
                    <th className="pb-3 font-medium">Category</th>
                    <th className="pb-3 font-medium">Product</th>
                    <th className="pb-3 font-medium">Units left</th>
                    <th className="pb-3 font-medium">Predicted demand ({horizon}d)</th>
                    <th className="pb-3 font-medium">Order quantity</th>
                    <th className="pb-3 font-medium">Based on</th>
                  </tr>
                </thead>
                <tbody>
                  {rows.map((r, i) => (
                    <motion.tr
                      key={r.product_id}
                      initial={{ opacity: 0, x: -16 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: i * 0.05 }}
                      className="border-b border-slate-100 last:border-0"
                    >
                      <td className="py-3 text-slate-500">{r.category_name ?? "—"}</td>
                      <td className="font-medium">{r.name}</td>
                      <td>
                        <span className="rounded-full bg-red-50 px-2.5 py-1 text-xs font-semibold text-red-700 ring-1 ring-red-200">
                          {r.current_stock} left
                        </span>
                      </td>
                      <td className="tabular-nums text-slate-600">
                        {r.predicted_demand === null ? "—" : r.predicted_demand.toFixed(1)}
                      </td>
                      <td className="text-lg font-bold tabular-nums text-indigo-700">{r.suggested_order_qty}</td>
                      <td>
                        {r.source === "forecast" ? (
                          <span className="rounded-full bg-indigo-50 px-2.5 py-1 text-xs font-medium text-indigo-700 ring-1 ring-indigo-200">
                            AI forecast
                          </span>
                        ) : (
                          <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-600 ring-1 ring-slate-200">
                            Simple rule (no sales history)
                          </span>
                        )}
                      </td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="mt-6 flex flex-wrap items-center justify-between gap-2 border-t border-slate-200 pt-4">
              <p className="text-xs text-slate-500">
                Order quantity = predicted demand + reorder level − units left. Supplier lead time is not modelled.
              </p>
              <p className="text-sm text-slate-600">
                Total to order: <span className="text-lg font-bold text-slate-900">{totalToOrder}</span> units
              </p>
            </div>
          </>
        )}
      </motion.div>
    </motion.div>
  );
}