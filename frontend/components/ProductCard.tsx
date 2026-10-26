"use client";

import { motion } from "motion/react";
import { CatalogItem } from "@/lib/api";

// placeholder pictures until real photos are added
const EMOJI: Record<string, string> = { electronics: "🔌", groceries: "🛒", stationery: "✏️" };
const TINTS = ["bg-indigo-50", "bg-emerald-50", "bg-amber-50", "bg-sky-50", "bg-fuchsia-50"];

type Props = {
  item: CatalogItem;
  index: number;
  busy: boolean; // true while a request for this product is in flight
  onSell: () => void;
  onRestock: () => void;
};

const stepBtn =
  "flex size-9 items-center justify-center rounded-lg bg-slate-100 text-lg font-semibold text-slate-700 transition disabled:cursor-not-allowed disabled:opacity-40";

export default function ProductCard({ item, index, busy, onSell, onRestock }: Props) {
  const low = item.current_stock <= item.reorder_level;
  const emoji = EMOJI[(item.category_name ?? "").toLowerCase()] ?? "📦";
  const tint = TINTS[(item.category_id ?? 0) % TINTS.length];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.04 }}
      whileHover={{ y: -4, boxShadow: "0 12px 24px rgba(15,23,42,0.08)" }}
      className="overflow-hidden rounded-2xl bg-white shadow-sm ring-1 ring-slate-200"
    >
      <div className={`flex h-40 items-center justify-center ${tint}`}>
        {item.image_url ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={item.image_url} alt={item.name} className="h-full w-full object-cover" />
        ) : (
          <span className="text-5xl">{emoji}</span>
        )}
      </div>

      <div className="space-y-2 p-4">
        <h3 className="font-semibold leading-tight">{item.name}</h3>
        <p className="text-xs text-slate-500">{item.sku}</p>
        <div className="flex items-center justify-between">
          <span className="text-lg font-semibold">₹{item.unit_price.toFixed(0)}</span>
          {low ? (
            <span className="rounded-full bg-red-50 px-2.5 py-1 text-xs font-medium text-red-700 ring-1 ring-red-200">
              Low stock
            </span>
          ) : (
            <span className="rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-700 ring-1 ring-emerald-200">
              In stock
            </span>
          )}
        </div>

        <div className="flex items-center justify-between pt-1">
          <motion.button
            whileTap={{ scale: 0.88 }}
            onClick={onSell}
            disabled={busy || item.current_stock === 0}
            title="Sold 1 unit"
            aria-label={`Sell one ${item.name}`}
            className={`${stepBtn} hover:bg-red-100 hover:text-red-700`}
          >
            −
          </motion.button>

          <p className="text-sm text-slate-600">
            {/* key = stock, so the number "pops" every time it changes */}
            <motion.span
              key={item.current_stock}
              initial={{ scale: 1.5 }}
              animate={{ scale: 1 }}
              className="inline-block text-lg font-semibold tabular-nums"
            >
              {item.current_stock}
            </motion.span>{" "}
            units
          </p>

          <motion.button
            whileTap={{ scale: 0.88 }}
            onClick={onRestock}
            disabled={busy}
            title="Restock 1 unit"
            aria-label={`Restock one ${item.name}`}
            className={`${stepBtn} hover:bg-emerald-100 hover:text-emerald-700`}
          >
            +
          </motion.button>
        </div>
      </div>
    </motion.div>
  );
}