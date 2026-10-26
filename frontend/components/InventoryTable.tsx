import { Product, Inventory } from "@/lib/api";

type Props = { products: Product[]; inventory: Inventory[] };

export default function InventoryTable({ products, inventory }: Props) {
  // product_id -> current_stock, so each product row can look up its stock
  const stockById = new Map(inventory.map((i) => [i.product_id, i.current_stock]));

  return (
    <section id="stock" className="scroll-mt-6 rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
      <h2 className="mb-4 text-lg font-semibold">Current Stock</h2>
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead className="text-xs uppercase tracking-wide text-slate-500">
            <tr className="border-b border-slate-200">
              <th className="pb-3 font-medium">Product</th>
              <th className="pb-3 font-medium">SKU</th>
              <th className="pb-3 font-medium">Stock</th>
              <th className="pb-3 font-medium">Reorder level</th>
              <th className="pb-3 font-medium">Status</th>
            </tr>
          </thead>
          <tbody>
            {products.map((p) => {
              const stock = stockById.get(p.id) ?? 0;
              const low = stock <= p.reorder_level;
              // bar is full when stock is 4x the reorder level
              const pct = Math.min(100, (stock / Math.max(p.reorder_level * 4, 1)) * 100);
              return (
                <tr key={p.id} className="border-b border-slate-100 last:border-0 hover:bg-slate-50">
                  <td className="py-3 font-medium">{p.name}</td>
                  <td className="text-slate-500">{p.sku}</td>
                  <td>
                    <div className="flex items-center gap-3">
                      <span className="w-10 tabular-nums">{stock}</span>
                      <div className="h-1.5 w-24 rounded-full bg-slate-100">
                        <div
                          className={`h-1.5 rounded-full ${low ? "bg-red-500" : "bg-emerald-500"}`}
                          style={{ width: `${pct}%` }}
                        />
                      </div>
                    </div>
                  </td>
                  <td className="text-slate-500">{p.reorder_level}</td>
                  <td>
                    {low ? (
                      <span className="rounded-full bg-red-50 px-2.5 py-1 text-xs font-medium text-red-700 ring-1 ring-red-200">
                        Low stock
                      </span>
                    ) : (
                      <span className="rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-700 ring-1 ring-emerald-200">
                        In stock
                      </span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
}