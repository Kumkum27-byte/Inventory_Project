"use client";

import { useState } from "react";
import { motion } from "motion/react";
import { Product, Inventory } from "@/lib/api";
import { usePolling } from "@/lib/usePolling";
import InventoryTable from "@/components/InventoryTable";
import ForecastCard from "@/components/ForecastCard";
import CountUp from "@/components/CountUp";
import SalesChart from "@/components/SalesChart";
import TopProducts from "@/components/TopProducts";
import LowStockDialog from "@/components/LowStockDialog";
import AppShell, { PageTitle } from "@/components/AppShell";

type StatProps = { icon: string; label: string; value: number; tone: string; delay: number; onClick?: () => void };

function StatCard({ icon, label, value, tone, delay, onClick }: StatProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      whileHover={{ y: -4, boxShadow: "0 12px 24px rgba(15,23,42,0.08)" }}
      onClick={onClick}
      className={`flex items-center gap-4 rounded-2xl bg-white p-5 shadow-sm ring-1 ring-slate-200 ${onClick ? "cursor-pointer" : ""}`}
    >
      <div className={`flex size-12 items-center justify-center rounded-xl text-xl ${tone}`}>{icon}</div>
      <div>
        <p className="text-sm text-slate-500">{label}</p>
        <p className="text-2xl font-semibold"><CountUp value={value} /></p>
      </div>
      {onClick && <span className="ml-auto text-xs text-slate-400">View plan →</span>}
    </motion.div>
  );
}

export default function Home() {
  // both lists refresh every 5 seconds, so stock numbers follow every sale
  const { data: products, error } = usePolling<Product[]>("/products/", 5000);
  const { data: inventory } = usePolling<Inventory[]>("/inventory/", 5000);
  const [showLow, setShowLow] = useState(false); // is the low-stock plan open

  if (error && !products) {
    return (
      <div className="p-10">
        <div className="rounded-2xl bg-red-50 p-6 text-red-700 ring-1 ring-red-200">
          Cannot load data: {error}. Is the FastAPI server running?
        </div>
      </div>
    );
  }

  const prods = products ?? [];
  const inv = inventory ?? [];
  const stockById = new Map(inv.map((i) => [i.product_id, i.current_stock]));
  const lowCount = prods.filter((p) => (stockById.get(p.id) ?? 0) <= p.reorder_level).length;
  const totalUnits = inv.reduce((sum, i) => sum + i.current_stock, 0);

  return (
    <AppShell>
      <PageTitle title="Dashboard" subtitle="Live stock levels and ML-powered demand forecasts" />
      <div className="space-y-8">
        <div className="grid gap-4 sm:grid-cols-3">
          <StatCard icon="📦" label="Products" value={prods.length} tone="bg-indigo-50" delay={0.1} />
          <StatCard icon="🧮" label="Units in stock" value={totalUnits} tone="bg-emerald-50" delay={0.2} />
          <StatCard icon="⚠️" label="Low stock" value={lowCount} tone="bg-red-50" delay={0.3} onClick={() => setShowLow(true)} />
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          <SalesChart />
          <TopProducts />
        </div>

        <ForecastCard products={prods} inventory={inv} />
        <InventoryTable products={prods} inventory={inv} />
      </div>
      <LowStockDialog open={showLow} onClose={() => setShowLow(false)} />
    </AppShell>
  );
}