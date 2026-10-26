"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

// Calls the API now and then again every `intervalMs`, so the screen stays fresh.
export function usePolling<T>(path: string, intervalMs = 5000) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [updatedAt, setUpdatedAt] = useState<number | null>(null);

  useEffect(() => {
    let cancelled = false; // stops late responses from updating an unmounted component

    async function load() {
      try {
        const result = await api<T>(path);
        if (!cancelled) {
          setData(result);
          setError(null);
          setUpdatedAt(Date.now());
        }
      } catch (e) {
        if (!cancelled) setError((e as Error).message);
      }
    }

    load();
    const id = setInterval(load, intervalMs);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, [path, intervalMs]);

  return { data, error, updatedAt };
}