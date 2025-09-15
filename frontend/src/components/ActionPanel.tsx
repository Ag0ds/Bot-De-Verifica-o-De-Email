"use client";

import { useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8000";

type GroqSuggestResponse = { draft_reply: string; category: string; confidence: number };
type SendIntentResponse = { request_id: string; masked_to: string };
type SendConfirmResponse = { queued: boolean };

export default function ActionPanel(props: { emailId: string; defaultToEmail?: string; initialDraft?: string }) {
  const [toEmail, setToEmail] = useState(props.defaultToEmail || "");
  const [draft, setDraft] = useState(props.initialDraft || "");
  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [requestId, setRequestId] = useState<string | null>(null);
  const [maskedTo, setMaskedTo] = useState<string | null>(null);
  const [otp, setOtp] = useState("");

  async function doSuggest() {
    setLoading("suggest"); setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/groq/suggest`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email_id: props.emailId }),
      });
      if (!res.ok) throw new Error(await res.text());
      const data: GroqSuggestResponse = await res.json();
      setDraft(data.draft_reply || "");
    } catch (e: any) {
      setError(e?.message || "Erro ao sugerir resposta");
    } finally {
      setLoading(null);
    }
  }

  async function doSendIntent() {
    setLoading("intent"); setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/send-intent`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email_id: props.emailId, to_email: toEmail, draft }),
      });
      if (!res.ok) throw new Error(await res.text());
      const data: SendIntentResponse = await res.json();
      setRequestId(data.request_id);
      setMaskedTo(data.masked_to);
    } catch (e: any) {
      setError(e?.message || "Erro ao solicitar envio");
    } finally {
      setLoading(null);
    }
  }

  async function doSendConfirm() {
    setLoading("confirm"); setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/send-confirm`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ request_id: requestId, otp }),
      });
      if (!res.ok) throw new Error(await res.text());
      const data: SendConfirmResponse = await res.json();
      alert(data.queued ? "Envio enfileirado/enviado ✅" : "Falha inesperada");
      setRequestId(null); setOtp(""); // reset estado
    } catch (e: any) {
      setError(e?.message || "Erro ao confirmar envio");
    } finally {
      setLoading(null);
    }
  }

  return (
    <section>
      <h3 style={{ fontSize: 14, marginBottom: 8 }}>Ações</h3>

      <div style={{ display: "grid", gap: 10 }}>
        <div>
          <button onClick={doSuggest} disabled={loading !== null} style={{ padding: "6px 10px" }}>
            {loading === "suggest" ? "Gerando..." : "Gerar rascunho (Groq)"}
          </button>
        </div>

        <div>
          <label style={{ display: "block", fontSize: 12, marginBottom: 4 }}>Destinatário permitido</label>
          <input value={toEmail} onChange={(e) => setToEmail(e.target.value)} placeholder="email@permitido.com"
            style={{ width: "100%", padding: 8, border: "1px solid #ccc", borderRadius: 6 }} />
        </div>

        <div>
          <label style={{ display: "block", fontSize: 12, marginBottom: 4 }}>Rascunho</label>
          <textarea value={draft} onChange={(e) => setDraft(e.target.value)}
            rows={8} style={{ width: "100%", padding: 8, border: "1px solid #ccc", borderRadius: 6, whiteSpace: "pre-wrap" }} />
        </div>

        <div>
          <button onClick={doSendIntent} disabled={loading !== null || !toEmail || !draft.trim()} style={{ padding: "6px 10px" }}>
            {loading === "intent" ? "Solicitando..." : "Solicitar envio (OTP)"}
          </button>
          {maskedTo && <p style={{ fontSize: 12, marginTop: 6 }}>Código enviado para: {maskedTo}</p>}
        </div>

        {requestId && (
          <div style={{ borderTop: "1px solid #eee", paddingTop: 10 }}>
            <label style={{ display: "block", fontSize: 12, marginBottom: 4 }}>OTP recebido</label>
            <input value={otp} onChange={(e) => setOtp(e.target.value)} placeholder="000000"
              style={{ width: 140, padding: 8, border: "1px solid #ccc", borderRadius: 6, marginRight: 8 }} />
            <button onClick={doSendConfirm} disabled={loading !== null || otp.length === 0} style={{ padding: "6px 10px" }}>
              {loading === "confirm" ? "Confirmando..." : "Confirmar envio"}
            </button>
          </div>
        )}

        {error && <p style={{ color: "crimson" }}>{error}</p>}
      </div>
    </section>
  );
}
