"use client"

import { useState } from "react"
import { Send, Sparkles, Mail, Shield, CheckCircle } from "lucide-react"

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8000"

type GroqSuggestResponse = { draft_reply: string; category: string; confidence: number }
type SendIntentResponse = { request_id: string; masked_to: string }
type SendConfirmResponse = { queued: boolean }

export default function ActionPanel(props: { emailId: string; defaultToEmail?: string; initialDraft?: string }) {
  const [toEmail, setToEmail] = useState(props.defaultToEmail || "")
  const [draft, setDraft] = useState(props.initialDraft || "")
  const [loading, setLoading] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const [requestId, setRequestId] = useState<string | null>(null)
  const [maskedTo, setMaskedTo] = useState<string | null>(null)
  const [otp, setOtp] = useState("")

  async function doSuggest() {
    setLoading("suggest")
    setError(null)
    try {
      const res = await fetch(`${API_BASE}/api/groq/suggest`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email_id: props.emailId }),
      })
      if (!res.ok) throw new Error(await res.text())
      const data: GroqSuggestResponse = await res.json()
      setDraft(data.draft_reply || "")
    } catch (e: unknown) {
      if (e instanceof Error) {
        setError(e.message)
      } else {
        setError("Erro ao sugerir resposta")
      }
    } finally {
      setLoading(null)
    }
  }

  async function doSendIntent() {
    setLoading("intent")
    setError(null)
    try {
      const res = await fetch(`${API_BASE}/api/send-intent`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email_id: props.emailId, to_email: toEmail, draft }),
      })
      if (!res.ok) throw new Error(await res.text())
      const data: SendIntentResponse = await res.json()
      setRequestId(data.request_id)
      setMaskedTo(data.masked_to)
    } catch (e: unknown) {
      if (e instanceof Error) {
        setError(e.message)
      } else {
        setError("Erro ao solicitar envio")
      }
    } finally {
      setLoading(null)
    }
  }

  async function doSendConfirm() {
    setLoading("confirm")
    setError(null)
    try {
      const res = await fetch(`${API_BASE}/api/send-confirm`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ request_id: requestId, otp }),
      })
      if (!res.ok) throw new Error(await res.text())
      const data: SendConfirmResponse = await res.json()
      alert(data.queued ? "Email enviado com sucesso!" : "Falha inesperada no envio")
      setRequestId(null)
      setOtp("")
    } catch (e: unknown) {
      if (e instanceof Error) {
        setError(e.message)
      } else {
        setError("Erro ao confirmar envio")
      }
    } finally {
      setLoading(null)
    }
  }

  return (
    <section>
      <h3 className="text-lg font-semibold text-purple-400 mb-6 flex items-center gap-2">
        <Send className="w-5 h-5" />
        Painel de Ações
      </h3>

      <div className="space-y-6">
        {/* AI Suggestion */}
        <div className="space-y-3">
          <button
            onClick={doSuggest}
            disabled={loading !== null}
            className="w-full flex items-center justify-center gap-2 bg-purple-600 hover:bg-purple-700 disabled:bg-purple-800 disabled:opacity-50 text-white px-4 py-3 rounded-lg font-medium transition-colors"
          >
            {loading === "suggest" ? (
              <>
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Gerando resposta...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                Gerar Rascunho com IA
              </>
            )}
          </button>
        </div>

        {/* Recipient */}
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-300 flex items-center gap-2">
            <Mail className="w-4 h-4" />
            Destinatário
          </label>
          <input
            value={toEmail}
            onChange={(e) => setToEmail(e.target.value)}
            placeholder="email@permitido.com"
            className="w-full px-4 py-3 bg-black/50 border border-gray-600 rounded-lg text-white placeholder-gray-500 focus:border-purple-500 focus:outline-none transition-colors"
          />
        </div>

        {/* Draft */}
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-300">Rascunho da Resposta</label>
          <textarea
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            rows={8}
            placeholder="Digite sua resposta aqui..."
            className="w-full px-4 py-3 bg-black/50 border border-gray-600 rounded-lg text-white placeholder-gray-500 focus:border-purple-500 focus:outline-none transition-colors resize-none"
          />
        </div>

        {/* Send Intent */}
        <div className="space-y-3">
          <button
            onClick={doSendIntent}
            disabled={loading !== null || !toEmail || !draft.trim()}
            className="w-full flex items-center justify-center gap-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-700 disabled:opacity-50 text-white px-4 py-3 rounded-lg font-medium transition-colors"
          >
            {loading === "intent" ? (
              <>
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Solicitando envio...
              </>
            ) : (
              <>
                <Shield className="w-4 h-4" />
                Solicitar Envio (OTP)
              </>
            )}
          </button>

          {maskedTo && (
            <div className="bg-blue-500/20 border border-blue-500/30 rounded-lg p-3">
              <p className="text-blue-400 text-sm flex items-center gap-2">
                <CheckCircle className="w-4 h-4" />
                Código OTP enviado para: <span className="font-mono">{maskedTo}</span>
              </p>
            </div>
          )}
        </div>

        {/* OTP Confirmation */}
        {requestId && (
          <div className="bg-gray-800/50 border border-gray-600 rounded-lg p-4 space-y-4">
            <h4 className="text-sm font-medium text-gray-300">Confirmação de Envio</h4>

            <div className="flex gap-3">
              <input
                value={otp}
                onChange={(e) => setOtp(e.target.value)}
                placeholder="000000"
                maxLength={6}
                className="flex-1 px-4 py-2 bg-black/50 border border-gray-600 rounded-lg text-white placeholder-gray-500 focus:border-purple-500 focus:outline-none transition-colors font-mono text-center"
              />
              <button
                onClick={doSendConfirm}
                disabled={loading !== null || otp.length === 0}
                className="px-6 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-700 disabled:opacity-50 text-white rounded-lg font-medium transition-colors flex items-center gap-2"
              >
                {loading === "confirm" ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Confirmando...
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    Confirmar
                  </>
                )}
              </button>
            </div>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="bg-red-950/50 border border-red-800/50 rounded-lg p-4">
            <p className="text-red-200 text-sm">{error}</p>
          </div>
        )}
      </div>
    </section>
  )
}
