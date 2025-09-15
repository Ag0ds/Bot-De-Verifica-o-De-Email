import Link from "next/link";
import { API_BASE } from "@/lib/api";

type EmailItem = {
  id?: string;
  email_id?: string;
  message_uid?: string;
  subject: string;
  category?: string;
  importance_label?: string;
  summary?: string;
  received_at?: string;
};

type ListResp = { items: EmailItem[]; page: number; limit: number };

function resolveOpenId(m: EmailItem): string {
  return m.id ?? m.message_uid ?? m.email_id ?? "";
}

export default async function Page() {
  const res = await fetch(`${API_BASE}/api/emails?limit=50`, { cache: "no-store" });
  if (!res.ok) {
    return (
      <main>
        <h2 style={{ fontSize: 18, marginBottom: 8 }}>Inbox</h2>
        <p>Falha ao carregar a lista.</p>
      </main>
    );
  }

  const data: ListResp = await res.json();
  const items: EmailItem[] = Array.isArray(data?.items) ? data.items : [];

  return (
    <main>
      <h2 style={{ fontSize: 18, marginBottom: 8 }}>Inbox</h2>

      <div style={{ display: "flex", gap: 8, marginBottom: 12 }}>
        <Link href="/" style={{ textDecoration: "underline" }}>Atualizar</Link>
      </div>

      {items.length === 0 && <p>Nenhum e-mail encontrado.</p>}

      <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "grid", gap: 10 }}>
        {items.map((m: EmailItem) => {
          const openId = resolveOpenId(m);
          return (
            <li key={openId || m.subject} style={{ border: "1px solid #ddd", padding: 12, borderRadius: 8 }}>
              <div style={{ display: "flex", justifyContent: "space-between", gap: 8 }}>
                <strong>{m.subject || "(sem assunto)"}</strong>
                <div style={{ display: "flex", gap: 6 }}>
                  {m.category && (
                    <span style={{ fontSize: 12, padding: "2px 6px", border: "1px solid #ccc", borderRadius: 999 }}>
                      {m.category}
                    </span>
                  )}
                  {m.importance_label && (
                    <span style={{ fontSize: 12, padding: "2px 6px", border: "1px solid #ccc", borderRadius: 999 }}>
                      {m.importance_label}
                    </span>
                  )}
                </div>
              </div>

              {m.summary && <p style={{ marginTop: 8, color: "#444" }}>{m.summary}</p>}

              <div style={{ marginTop: 8, display: "flex", alignItems: "center", gap: 8 }}>
                {openId ? (
                  <Link href={`/email/${encodeURIComponent(openId)}`}>Abrir</Link>
                ) : (
                  <span style={{ color: "#999" }}>Sem ID para abrir</span>
                )}
                <small style={{ color: "#666" }}>
                  id: {m.id ?? "—"} | uid: {m.message_uid ?? "—"}
                </small>
              </div>
            </li>
          );
        })}
      </ul>
    </main>
  );
}
