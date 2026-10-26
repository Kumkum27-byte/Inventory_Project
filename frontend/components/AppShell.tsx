"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "motion/react";
import type { ReactNode } from "react";

const NAV = [
  { href: "/", label: "Dashboard" },
  { href: "/inventory", label: "Inventory" },
];

// Sidebar + page frame shared by every page
export default function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname(); // current URL, used to highlight the active link

  return (
    <div className="flex min-h-screen bg-slate-50 text-slate-900">
      <motion.aside
        initial={{ x: -40, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="sticky top-0 hidden h-screen w-60 shrink-0 flex-col bg-slate-900 p-6 text-slate-300 md:flex"
      >
        <div className="mb-10 text-lg font-semibold text-white">📦 Inventory AI</div>
        <nav className="space-y-1 text-sm">
          {NAV.map((item) => (
            <motion.div key={item.href} whileHover={{ x: 4 }}>
              <Link
                href={item.href}
                className={`block rounded-lg px-3 py-2 ${
                  pathname === item.href ? "bg-slate-800 text-white" : "hover:bg-slate-800"
                }`}
              >
                {item.label}
              </Link>
            </motion.div>
          ))}
        </nav>
      </motion.aside>

      <main className="relative min-w-0 flex-1 overflow-hidden p-6 md:p-10">
        {/* slowly floating background blobs */}
        <motion.div
          animate={{ y: [0, -24, 0], x: [0, 16, 0] }}
          transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
          className="pointer-events-none absolute -top-16 right-10 size-72 rounded-full bg-indigo-300/30 blur-3xl"
        />
        <motion.div
          animate={{ y: [0, 20, 0], x: [0, -20, 0] }}
          transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
          className="pointer-events-none absolute top-40 -left-10 size-64 rounded-full bg-fuchsia-300/20 blur-3xl"
        />
        <div className="relative z-10">{children}</div>
      </main>
    </div>
  );
}

export function PageTitle({ title, subtitle }: { title: string; subtitle: string }) {
  return (
    <motion.header
      initial={{ opacity: 0, y: -16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="mb-8"
    >
      <h1
        className="bg-clip-text text-4xl font-bold tracking-tight text-transparent"
        style={{ backgroundImage: "linear-gradient(90deg, #4f46e5, #d946ef)" }}
      >
        {title}
      </h1>
      <p className="text-slate-500">{subtitle}</p>
    </motion.header>
  );
}