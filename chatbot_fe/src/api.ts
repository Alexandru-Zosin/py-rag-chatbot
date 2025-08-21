const API_BASE =
  (import.meta.env.VITE_API_BASE as string | undefined) || "/api";

async function postJSON<T>(path: string, body: unknown): Promise<T> {
  const ctrl = new AbortController();
  const id = setTimeout(() => ctrl.abort(), 60000);
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal: ctrl.signal,
    });
    if (!res.ok) {
      const text = await res.text().catch(() => "");
      throw new Error(`HTTP ${res.status}: ${text}`);
    }
    return (await res.json()) as T;
  } finally {
    clearTimeout(id);
  }
}

export async function chat(query: string, k: number): Promise<{
  answer: string;
  sources: Array<Record<string, unknown>>;
}> {
  return postJSON("/chat", { query, k });
}
