import { useEffect, useMemo, useRef, useState } from "react";
import { chat } from "./api";
import type { ChatResponse } from "./types";

type Message = {
  id: string;
  role: "user" | "librarian";
  text: string;
  sources?: ChatResponse["sources"];
};

function uid() {
  return Math.random().toString(36).slice(2);
}

export default function App() {
  const [query, setQuery] = useState("");
  const [k, setK] = useState(4);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const listRef = useRef<HTMLDivElement>(null);

  const canSend = useMemo(
    () => query.trim().length > 0 && !loading,
    [query, loading]
  );

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: "smooth" });
  }, [messages.length]);

  async function onAsk(e: React.FormEvent) {
    e.preventDefault();
    const q = query.trim();
    if (!q) return;
    setError(null);
    setLoading(true);
    const userMsg: Message = { id: uid(), role: "user", text: q };
    setMessages((m) => [...m, userMsg]);
    try {
      const resp = await chat(q, k);
      const botMsg: Message = {
        id: uid(),
        role: "librarian",
        text: resp.answer,
        sources: resp.sources,
      };
      setMessages((m) => [...m, botMsg]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed");
    } finally {
      setLoading(false);
      setQuery("");
    }
  }

  return (
    <div style={styles.shell}>
      <aside style={styles.sidebar}>
        <div style={styles.brand}>
          <div style={styles.avatar}>L</div>
          <div>
            <div style={styles.brandTitle}>Library Assistant</div>
            <div style={styles.brandSub}>Chroma + OpenAI</div>
          </div>
        </div>
        <div style={styles.note}>
          Tip: include the word "summary" to trigger the summary tool.
        </div>
      </aside>

      <main style={styles.main}>
        <div style={styles.header}>Ask the librarian</div>

        <div ref={listRef} style={styles.messages}>
          {messages.map((m) => (
            <div key={m.id} style={m.role === "user" ? styles.msgUser : styles.msgBot}>
              <div style={styles.msgRole}>{m.role === "user" ? "You" : "Librarian"}</div>
              <div style={styles.msgText}>{m.text}</div>
              {m.sources && m.sources.length > 0 && (
                <details style={styles.sources}>
                  <summary>Sources ({m.sources.length})</summary>
                  <ol>
                    {m.sources.map((s, i) => (
                      <li key={i} style={styles.sourceItem}>
                        <code style={styles.code}>{JSON.stringify(s)}</code>
                      </li>
                    ))}
                  </ol>
                </details>
              )}
            </div>
          ))}
        </div>

        <form onSubmit={onAsk} style={styles.form}>
          <input
            type="text"
            placeholder="Ask about a book... e.g. 'summary of 1984'"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            style={styles.input}
            disabled={loading}
          />
          <label style={styles.kLabel}>
            k:
            <input
              type="number"
              min={1}
              max={12}
              value={k}
              onChange={(e) => setK(Number(e.target.value))}
              style={styles.kInput}
            />
          </label>
          <button type="submit" disabled={!canSend} style={styles.button}>
            {loading ? "Asking..." : "Ask"}
          </button>
        </form>

        {error && <div style={styles.error}>Error: {error}</div>}
      </main>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  shell: {
    display: "grid",
    gridTemplateColumns: "280px 1fr",
    height: "100%",
    background: "#f6f7fb",
  },
  sidebar: {
    padding: "20px",
    borderRight: "1px solid #e5e7eb",
    background: "#fff",
  },
  brand: {
    display: "flex",
    gap: "12px",
    alignItems: "center",
    marginBottom: "16px",
  },
  avatar: {
    width: "40px",
    height: "40px",
    borderRadius: "8px",
    background: "#111827",
    color: "#fff",
    display: "grid",
    placeItems: "center",
    fontWeight: 700,
  },
  brandTitle: { fontSize: "16px", fontWeight: 700 },
  brandSub: { fontSize: "12px", color: "#6b7280" },
  note: {
    fontSize: "12px",
    color: "#374151",
    background: "#f3f4f6",
    padding: "10px",
    borderRadius: "8px",
  },
  main: {
    display: "grid",
    gridTemplateRows: "auto 1fr auto auto",
    gap: "12px",
    height: "100%",
    padding: "16px 20px",
  },
  header: { fontSize: "18px", fontWeight: 700 },
  messages: {
    overflowY: "auto",
    background: "#ffffff",
    border: "1px solid #e5e7eb",
    borderRadius: "10px",
    padding: "12px",
  },
  msgUser: {
    padding: "10px",
    marginBottom: "10px",
    background: "#ecfeff",
    border: "1px solid #bae6fd",
    borderRadius: "8px",
  },
  msgBot: {
    padding: "10px",
    marginBottom: "10px",
    background: "#eef2ff",
    border: "1px solid #c7d2fe",
    borderRadius: "8px",
  },
  msgRole: { fontSize: "12px", color: "#6b7280", marginBottom: "6px" },
  msgText: { whiteSpace: "pre-wrap", fontSize: "14px", lineHeight: 1.5 },
  sources: { marginTop: "8px" },
  sourceItem: { margin: "6px 0" },
  code: {
    fontFamily: "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace",
    fontSize: "12px",
    background: "#f9fafb",
    padding: "4px 6px",
    borderRadius: "6px",
    display: "inline-block",
  },
  form: {
    display: "grid",
    gridTemplateColumns: "1fr auto auto",
    gap: "8px",
    alignItems: "center",
  },
  input: {
    padding: "10px 12px",
    borderRadius: "8px",
    border: "1px solid #d1d5db",
    fontSize: "14px",
    outline: "none",
  },
  kLabel: { fontSize: "12px", color: "#374151" },
  kInput: {
    width: "56px",
    marginLeft: "6px",
    padding: "6px",
    borderRadius: "6px",
    border: "1px solid #d1d5db",
  },
  button: {
    padding: "10px 14px",
    borderRadius: "8px",
    border: "1px solid #111827",
    background: "#111827",
    color: "#fff",
    cursor: "pointer",
  },
  error: {
    color: "#b91c1c",
    background: "#fee2e2",
    border: "1px solid #fecaca",
    borderRadius: "8px",
    padding: "8px 10px",
  },
};
