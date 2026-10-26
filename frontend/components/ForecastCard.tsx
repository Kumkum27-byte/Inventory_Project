"use client";

import { useState } from "react";
import {
  CartesianGrid, Legend, Line, LineChart,
  ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";
import { api, Product, Inventory, DailySale, Forecast } from "@/lib/api";

type Point = { date: string; actual?: number; forecast?: number };
type Summary = { stock: number; demand: number; suggested: number };
type Props = { products: Product[]; inventory: Inventory[] };

const field =
  "rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500";

export default function ForecastCard({ products, inventory }: Props) {
  const [productId, setProductId] = useState<number | null>(null);
  const [horizon, setHorizon] = useState(7);
  const [points, setPoints] = useState<Point[]>([]);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // until the user picks something, default to the first product
  const selectedId = productId ?? products[0]?.id;

  async function generate() {
    if (selectedId === undefined) return;
    setLoading(true);
    setError(null);
    try {
      // both calls run at the same time
      const [history, fc] = await Promise.all([
        api<DailySale[]>(`/sales/daily/${selectedId}?days=30`),
        api<Forecast>(`/forecasts/${selectedId}?horizon=${horizon}`),
      ]);

      // merge past sales and forecast into one list, keyed by date
      const byDate = new Map<string, Point>();
      history.forEach((h) => byDate.set(h.date, { date: h.date, actual: h.quantity }));
      fc.forecast.forEach((f) =>
        byDate.set(f.date, { ...byDate.get(f.date), date: f.date, forecast: f.predicted_quantity })
      );
      setPoints([...byDate.values()].sort((a, b) => a.date.localeCompare(b.date)));

      const product = products.find((p) => p.id === selectedId);
      const stock = inventory.find((i) => i.product_id === selectedId)?.current_stock ?? 0;
      const demand = fc.total_predicted_demand;
      // simple rule: demand + safety buffer (reorder level) - stock on hand
      const suggested = Math.max(0, Math.round(demand + (product?.reorder_level ?? 0) - stock));
      setSummary({ stock, demand, suggested });
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section id="forecast" className="scroll-mt-6 rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
      <h2 className="mb-4 text-lg font-semibold">Demand Forecast</h2>

      <div className="mb-6 flex flex-wrap items-center gap-3">
        <select className={field} value={selectedId ?? ""} onChange={(e) => setProductId(Number(e.target.value))}>
          {products.map((p) => (
            <option key={p.id} value={p.id}>{p.name} ({p.sku})</option>
          ))}
        </select>
        <select className={field} value={horizon} onChange={(e) => setHorizon(Number(e.target.value))}>
          {[7, 30, 90].map((d) => (
            <option key={d} value={d}>{d} days</option>
          ))}
        </select>
        <button
          onClick={generate}
          disabled={loading || selectedId === undefined}
          className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500 disabled:opacity-50"
        >
          {loading ? "Loading..." : "Generate forecast"}
        </button>
      </div>

      {error && <p className="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</p>}

      {!summary && !error && (
        <div className="rounded-xl border border-dashed border-slate-300 p-10 text-center text-sm text-slate-500">
          Pick a product and click “Generate forecast” to see predicted demand.
        </div>
      )}

      {summary && (
        <>
          <div className="mb-6 grid gap-4 sm:grid-cols-3">
            <Metric label="Current stock" value={summary.stock} />
            <Metric label={`Predicted demand (${horizon} days)`} value={Math.round(summary.demand * 10) / 10} />
            <Metric label="Suggested order qty" value={summary.suggested} highlight={summary.suggested > 0} />
          </div>
          <ResponsiveContainer width="100%" height={320}>
            <LineChart data={points}>
              <CartesianGrid vertical={false} stroke="#e2e8f0" />
              <XAxis dataKey="date" tickFormatter={(d: string) => d.slice(5)} tickLine={false} axisLine={false} />
              <YAxis tickLine={false} axisLine={false} />
              <Tooltip contentStyle={{ borderRadius: 12, border: "1px solid #e2e8f0" }} />
              <Legend />
              <Line type="monotone" dataKey="actual" name="Actual" stroke="#4f46e5" strokeWidth={2.5} dot={false} />
              <Line type="monotone" dataKey="forecast" name="Forecast" stroke="#f97316" strokeWidth={2.5} strokeDasharray="6 4" dot={false} />
            </LineChart>
          </ResponsiveContainer>
          <p className="mt-3 text-xs text-slate-500">
            Suggested order = predicted demand + reorder level - current stock. Supplier lead time is not modelled.
          </p>
        </>
      )}
    </section>
  );
}

function Metric({ label, value, highlight = false }: { label: string; value: number; highlight?: boolean }) {
  return (
    <div className={`rounded-xl p-4 ring-1 ${highlight ? "bg-indigo-50 ring-indigo-200" : "bg-slate-50 ring-slate-200"}`}>
      <div className="text-sm text-slate-500">{label}</div>
      <div className={`text-3xl font-semibold ${highlight ? "text-indigo-700" : ""}`}>{value}</div>
    </div>
  );
}