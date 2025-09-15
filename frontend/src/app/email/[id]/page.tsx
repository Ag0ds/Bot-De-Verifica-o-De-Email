import { API_BASE } from "@/lib/api";
import ActionPanel from "@/components/ActionPanel";
import Link from "next/link";

type EmailAttachment = {
  filename?: string;
  content_type?: string;
  size?: number;
};

type EmailContent = {
  body_text?: string;
  body_html?: string;
  attachments?: EmailAttachment[];
};

type EmailResp = {
  meta: {
    id: string;
    subject: string;
    category?: string;
    importance_label?: string;
    reply_suggested?: string;
    received_at?: string;
    from_email?: string;
    summary?: string;
    message_uid?: string;
  };
  content: EmailContent | null;
};

export default async function EmailPage({
  params,
}: {
  params: Promise<{ id: string }>;
  searchParams?: Promise<Record<string, string | string[] | undefined>>;
}) {
  const { id } = await params; 
  const url = `${API_BASE}/api/emails/${encodeURIComponent(id)}`;
  const res = await fetch(url, { cache: "no-store" });

  if (!res.ok) {
    const txt = await res.text().catch(() => "");
    return (
      <main>
        <Link href="/" style={{ textDecoration: "underline" }}>
          ← Voltar
        </Link>
        <h2 style={{ fontSize: 18 }}>Não encontrado (debug)</h2>
        <pre
          style={{
            whiteSpace: "pre-wrap",
            background: "#fafafa",
            border: "1px solid #eee",
            padding: 10,
          }}
        >{`params.id: ${id}
URL: ${url}
status: ${res.status}
body:
${txt}`}</pre>
      </main>
    );
  }

  const data: EmailResp = await res.json();
  const m = data.meta;
  const c: EmailContent = data.content ?? {}; 

  const attachments: EmailAttachment[] = c.attachments ?? [];

  return (
    <main>
      <Link href="/" style={{ textDecoration: "underline" }}>
        ← Voltar
      </Link>

      <h2 style={{ fontSize: 18, margin: "8px 0" }}>
        {m.subject || "(sem assunto)"}
      </h2>

      <div style={{ display: "flex", gap: 8, marginBottom: 8 }}>
        {m.category && (
          <span
            style={{
              fontSize: 12,
              padding: "2px 6px",
              border: "1px solid #ccc",
              borderRadius: 999,
            }}
          >
            {m.category}
          </span>
        )}
        {m.importance_label && (
          <span
            style={{
              fontSize: 12,
              padding: "2px 6px",
              border: "1px solid #ccc",
              borderRadius: 999,
            }}
          >
            {m.importance_label}
          </span>
        )}
      </div>

      {m.summary && (
        <>
          <h3 style={{ fontSize: 14, marginTop: 8 }}>Resumo</h3>
          <p>{m.summary}</p>
        </>
      )}

      <h3 style={{ fontSize: 14, marginTop: 8 }}>Corpo (texto)</h3>
      <pre
        style={{
          whiteSpace: "pre-wrap",
          background: "#fafafa",
          border: "1px solid #eee",
          padding: 10,
          borderRadius: 6,
        }}
      >
        {c.body_text || "(vazio)"}
      </pre>

      {attachments.length > 0 && (
        <>
          <h3 style={{ fontSize: 14, marginTop: 8 }}>Anexos</h3>
          <ul>
            {attachments.map((a, i) => (
              <li key={i}>
                {a.filename} {a.content_type ? `(${a.content_type})` : ""}{" "}
                {typeof a.size === "number" ? `- ${a.size} bytes` : ""}
              </li>
            ))}
          </ul>
        </>
      )}

      <hr style={{ margin: "16px 0" }} />

      <ActionPanel
        emailId={m.id}
        defaultToEmail="bbitteste@gmail.com"
        initialDraft={m.reply_suggested || ""}
      />
    </main>
  );
}
