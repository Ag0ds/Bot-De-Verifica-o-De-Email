import Link from "next/link";
import { API_BASE } from "@/lib/api";

type EmailItem = {
  id: string;
  subject: string;
  category?: string;
  importance_label?: string;
  summary?: string;
  received_at?: string;
};

type ListResp = { items: EmailItem[]; page: number; limit: number };

export default async function Page() {
  const res = await fetch(`${API_BASE}/api/emails?limit=50`, { cache: "no-store" });
  const data: ListResp = await res.json();
  const items = data.items || [];

  return (
    <main>
      <h2 style={{ fontSize: 18, marginBottom: 8 }}>Inbox</h2>

      <div style={{ display: "flex", gap: 8, marginBottom: 12 }}>
        <a href="/" style={{ textDecoration: "underline" }}>Atualizar</a>
      </div>

      {items.length === 0 && <p>Nenhum e-mail encontrado.</p>}

      <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "grid", gap: 10 }}>
        {items.map((m) => (
          <li key={m.id} style={{ border: "1px solid #ddd", padding: 12, borderRadius: 8 }}>
            <div style={{ display: "flex", justifyContent: "space-between", gap: 8 }}>
              <strong>{m.subject || "(sem assunto)"}</strong>
              <div style={{ display: "flex", gap: 6 }}>
                {m.category && <span style={{ fontSize: 12, padding: "2px 6px", border: "1px solid #ccc", borderRadius: 999 }}>{m.category}</span>}
                {m.importance_label && <span style={{ fontSize: 12, padding: "2px 6px", border: "1px solid #ccc", borderRadius: 999 }}>{m.importance_label}</span>}
              </div>
            </div>
            {m.summary && <p style={{ marginTop: 8, color: "#444" }}>{m.summary}</p>}

            <div style={{ marginTop: 8 }}>
              <Link href={`/email/${(m as any).id ?? (m as any).email_id ?? (m as any).message_uid}`}>
                Abrir
              </Link>
              <small style={{color:"#666"}}>
                id: {(m as any).id} | uid: {(m as any).message_uid}
              </small>
            </div>
          </li>
        ))}
      </ul>
    </main>
  );
}
