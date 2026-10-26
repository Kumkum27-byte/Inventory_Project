export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

// Shapes of the JSON the FastAPI backend returns
export type Product = {
  id: number;
  name: string;
  sku: string;
  reorder_level: number;
  unit_price: number;
};
export type Inventory = { product_id: number; current_stock: number };
export type Category = { id: number; name: string };
export type CatalogItem = {
  id: number;
  name: string;
  sku: string;
  image_url: string | null;
  unit_price: number;
  reorder_level: number;
  category_id: number | null;
  category_name: string | null;
  current_stock: number;
};
export type DailySale = { date: string; quantity: number };
export type Forecast = {
  product_id: number;
  horizon_days: number;
  forecast: { date: string; predicted_quantity: number }[];
  total_predicted_demand: number;
};

// One helper for every GET call: fetch, check status, return typed JSON
export async function api<T>(path: string): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, { cache: "no-store" });
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(
      typeof body?.detail === "string" ? body.detail : `Request failed (${res.status})`
    );
  }
  return res.json() as Promise<T>;
}

// POST helper: sends JSON, returns the parsed JSON response
export async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => null);
    throw new Error(
      typeof err?.detail === "string"
        ? err.detail
        : Array.isArray(err?.detail)
          ? err.detail.map((d: { msg: string }) => d.msg).join("; ")
          : `Request failed (${res.status})`
    );
  }
  return res.json() as Promise<T>;
}