"use client";

import { useEffect, useState } from "react";
import { motion } from "motion/react";
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { usePolling } from "@/lib/usePolling";

type Day = { date: string; units: number };

export default function SalesChart() {
  const { data, error, updatedAt } = usePolling<Day[]>("/sales/daily?days=30", 5000);

  // a clock that ticks every second, only to show "updated 3s ago"
  const [now, setNow] = useState<number | null>(null); // null until the browser starts the clock
  useEffect(() => {
    const id = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(id);
  }, []);
  const secs =
    updatedAt === null || now === null ? null : Math.max(0, Math.round((now - updatedAt) / 1000));

  const days = data ?? [];
  const today = days.length ? days[days.length - 1].units : 0;
  const total = days.reduce((sum, d) => sum + d.units, 0);

  return (
    <motion.section
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.35 }}
      className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200 lg:col-span-2"
    >
      <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold">Sales per day</h2>
          <p className="text-xs text-slate-500">Units sold, last 30 days</p>
        </div>
        <span
          className={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-medium ring-1 ${
            error ? "bg-red-50 text-red-700 ring-red-200" : "bg-emerald-50 text-emerald-700 ring-emerald-200"
          }`}
        >
          <span className="relative flex size-2">
            {!error && (
              <span className="absolute inline-flex size-full animate-ping rounded-full bg-emerald-400 opacity-75" />
            )}
            <span className={`relative inline-flex size-2 rounded-full ${error ? "bg-red-500" : "bg-emerald-500"}`} />
          </span>
          {error ? "Offline" : secs === null ? "Connecting..." : `Live · updated ${secs}s ago`}
        </span>
      </div>

      <div className="mb-4 flex gap-8">
        <div>
          <p className="text-xs text-slate-500">Today</p>
          {/* key = value, so the number pops whenever it changes */}
          <motion.p key={today} initial={{ scale: 1.3 }} animate={{ scale: 1 }} className="origin-left text-2xl font-semibold tabular-nums">
            {today}
          </motion.p>
        </div>
        <div>
          <p className="text-xs text-slate-500">Last 30 days</p>
          <p className="text-2xl font-semibold tabular-nums">{total}</p>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={260}>
        <AreaChart data={days}>
          <defs>
            <linearGradient id="salesFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#4f46e5" stopOpacity={0.35} />
              <stop offset="95%" stopColor="#4f46e5" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid vertical={false} stroke="#e2e8f0" />
          <XAxis dataKey="date" tickFormatter={(d: string) => d.slice(5)} tickLine={false} axisLine={false} minTickGap={24} />
          <YAxis tickLine={false} axisLine={false} width={32} />
          <Tooltip contentStyle={{ borderRadius: 12, border: "1px solid #e2e8f0" }} />
          <Area
            type="monotone"
            dataKey="units"
            name="Units sold"
            stroke="#4f46e5"
            strokeWidth={2.5}
            fill="url(#salesFill)"
            isAnimationActive={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </motion.section>
  );
}