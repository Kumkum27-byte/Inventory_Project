"use client";

import { useEffect, useState } from "react";
import { api, post, Category, CatalogItem } from "@/lib/api";
import AppShell, { PageTitle } from "@/components/AppShell";
import ProductCard from "@/components/ProductCard";
import AddProductDialog from "@/components/AddProductDialog";

export default function InventoryPage() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [items, setItems] = useState<CatalogItem[]>([]);
  const [selected, setSelected] = useState<number | null>(null); // null = all items
  const [error, setError] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<number | null>(null); // product with a request in flight
  const [notice, setNotice] = useState<string | null>(null); // error from a - or + click
  const [showAdd, setShowAdd] = useState(false); // is the "Add product" form open

  // load everything once; clicking a category then filters in the browser (instant)
  useEffect(() => {
    Promise.all([api<Category[]>("/categories/"), api<CatalogItem[]>("/inventory/catalog")])
      .then(([c, i]) => {
        setCategories(c);
        setItems(i);
      })
      .catch((e) => setError(e.message));
  }, []);

  // run a request, then reload the stock numbers from the server
  async function act(id: number, run: () => Promise<unknown>) {
    setBusyId(id);
    setNotice(null);
    try {
      await run();
      setItems(await api<CatalogItem[]>("/inventory/catalog"));
    } catch (e) {
      setNotice((e as Error).message);
    } finally {
      setBusyId(null);
    }
  }

  // "-" = one unit sold (creates a sale, stock goes down automatically)
  const sellOne = (id: number) => act(id, () => post("/sales/", { product_id: id, quantity: 1 }));
  // "+" = one unit restocked
  const restockOne = (id: number) =>
    act(id, () =>
      post("/inventory/stock-movement", { product_id: id, movement_type: "stock_in", quantity: 1 })
    );

  // after a product is saved: close the form, show all items, reload the cards
  async function productCreated() {
    setShowAdd(false);
    setSelected(null);
    try {
      setItems(await api<CatalogItem[]>("/inventory/catalog"));
    } catch (e) {
      setNotice((e as Error).message);
    }
  }

  const visible = selected === null ? items : items.filter((i) => i.category_id === selected);
  const countFor = (id: number) => items.filter((i) => i.category_id === id).length;

  const btn = (active: boolean) =>
    `flex w-full items-center justify-between rounded-lg px-3 py-2 text-left text-sm transition ${
      active ? "bg-indigo-600 text-white" : "text-slate-700 hover:bg-slate-100"
    }`;

  return (
    <AppShell>
      <PageTitle title="Inventory" subtitle="Browse your products by category" />

      {error ? (
        <div className="rounded-2xl bg-red-50 p-6 text-red-700 ring-1 ring-red-200">
          Cannot load data: {error}. Is the FastAPI server running?
        </div>
      ) : (
        <div className="flex flex-col gap-6 md:flex-row">
          <div className="space-y-1 self-start rounded-2xl bg-white p-3 shadow-sm ring-1 ring-slate-200 md:w-56 md:shrink-0">
            <button className={btn(selected === null)} onClick={() => setSelected(null)}>
              <span>All items</span>
              <span className="text-xs opacity-70">{items.length}</span>
            </button>
            {categories.map((c) => (
              <button key={c.id} className={btn(selected === c.id)} onClick={() => setSelected(c.id)}>
                <span>{c.name}</span>
                <span className="text-xs opacity-70">{countFor(c.id)}</span>
              </button>
            ))}
          </div>

          <div className="flex-1 space-y-4">
            <div className="flex items-center justify-between">
              <p className="text-sm text-slate-500">{visible.length} products</p>
              <button
                onClick={() => setShowAdd(true)}
                className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-indigo-500 active:scale-95"
              >
                + Add product
              </button>
            </div>
            {notice && (
              <p className="rounded-lg bg-red-50 p-3 text-sm text-red-700 ring-1 ring-red-200">{notice}</p>
            )}
            <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-3">
              {visible.map((item, i) => (
                <ProductCard
                  key={item.id}
                  item={item}
                  index={i}
                  busy={busyId === item.id}
                  onSell={() => sellOne(item.id)}
                  onRestock={() => restockOne(item.id)}
                />
              ))}
              {visible.length === 0 && (
                <p className="col-span-full text-sm text-slate-500">No products in this category.</p>
              )}
            </div>
          </div>
        </div>
      )}
      <AddProductDialog
        open={showAdd}
        categories={categories}
        onClose={() => setShowAdd(false)}
        onCreated={productCreated}
      />
    </AppShell>
  );
}