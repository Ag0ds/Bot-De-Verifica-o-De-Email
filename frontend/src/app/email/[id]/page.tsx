import { API_BASE } from "@/lib/api"
import ActionPanel from "@/components/ActionPanel"
import Link from "next/link"
import { ArrowLeft, Mail, Paperclip } from "lucide-react"

type EmailAttachment = {
  filename?: string
  content_type?: string
  size?: number
}

type EmailContent = {
  body_text?: string
  body_html?: string
  attachments?: EmailAttachment[]
}

type EmailResp = {
  meta: {
    id: string
    subject: string
    category?: string
    importance_label?: string
    reply_suggested?: string
    received_at?: string
    from_email?: string
    summary?: string
    message_uid?: string
  }
  content: EmailContent | null
}

export default async function EmailPage({
  params,
}: {
  params: Promise<{ id: string }>
  searchParams?: Promise<Record<string, string | string[] | undefined>>
}) {
  const { id } = await params
  const url = `${API_BASE}/api/emails/${encodeURIComponent(id)}`
  const res = await fetch(url, { cache: "no-store" })

  if (!res.ok) {
    const txt = await res.text().catch(() => "")
    return (
      <main className="min-h-screen bg-black text-white p-6">
        <div className="max-w-4xl mx-auto">
          <Link
            href="/"
            className="inline-flex items-center gap-2 text-purple-400 hover:text-purple-300 transition-colors mb-6"
          >
            <ArrowLeft className="w-4 h-4" />
            Voltar
          </Link>

          <div className="bg-red-950/50 border border-red-800/50 rounded-lg p-6">
            <h2 className="text-xl font-semibold text-red-200 mb-4">Email não encontrado</h2>
            <div className="bg-gray-900/50 border border-gray-700 rounded-lg p-4 font-mono text-sm text-gray-300">
              <div className="whitespace-pre-wrap">
                {`ID: ${id}
URL: ${url}
Status: ${res.status}
Resposta:
${txt}`}
              </div>
            </div>
          </div>
        </div>
      </main>
    )
  }

  const data: EmailResp = await res.json()
  const m = data.meta
  const c: EmailContent = data.content ?? {}
  const attachments: EmailAttachment[] = c.attachments ?? []

  const getCategoryColor = (category?: string) => {
    switch (category?.toLowerCase()) {
      case "produtivo":
        return "bg-green-500/20 text-green-400 border-green-500/30"
      case "improdutivo":
        return "bg-red-500/20 text-red-400 border-red-500/30"
      default:
        return "bg-gray-500/20 text-gray-400 border-gray-500/30"
    }
  }

  const getImportanceColor = (importance?: string) => {
    switch (importance?.toLowerCase()) {
      case "alta":
      case "high":
        return "bg-orange-500/20 text-orange-400 border-orange-500/30"
      case "média":
      case "medium":
        return "bg-yellow-500/20 text-yellow-400 border-yellow-500/30"
      case "baixa":
      case "low":
        return "bg-blue-500/20 text-blue-400 border-blue-500/30"
      default:
        return "bg-gray-500/20 text-gray-400 border-gray-500/30"
    }
  }

  return (
    <main className="min-h-screen bg-black text-white">
      <div className="max-w-4xl mx-auto p-6">
        {/* Header */}
        <div className="mb-8">
          <Link
            href="/"
            className="inline-flex items-center gap-2 text-purple-400 hover:text-purple-300 transition-colors mb-6"
          >
            <ArrowLeft className="w-4 h-4" />
            Voltar
          </Link>

          <div className="flex items-start gap-4 mb-4">
            <div className="p-3 bg-purple-500/20 rounded-lg border border-purple-500/30">
              <Mail className="w-6 h-6 text-purple-400" />
            </div>
            <div className="flex-1">
              <h1 className="text-2xl font-bold text-white mb-2 text-balance">{m.subject || "(sem assunto)"}</h1>
              {m.from_email && <p className="text-gray-400 text-sm">De: {m.from_email}</p>}
              {m.received_at && (
                <p className="text-gray-500 text-xs mt-1">
                  Recebido em: {new Date(m.received_at).toLocaleString("pt-BR")}
                </p>
              )}
            </div>
          </div>

          {/* Tags */}
          <div className="flex flex-wrap gap-2">
            {m.category && (
              <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getCategoryColor(m.category)}`}>
                {m.category}
              </span>
            )}
            {m.importance_label && (
              <span
                className={`px-3 py-1 rounded-full text-xs font-medium border ${getImportanceColor(m.importance_label)}`}
              >
                {m.importance_label}
              </span>
            )}
          </div>
        </div>

        {/* Content */}
        <div className="space-y-6">
          {/* Summary */}
          {m.summary && (
            <div className="bg-gray-900/50 border border-gray-700 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-purple-400 mb-3">Resumo</h3>
              <p className="text-gray-300 leading-relaxed">{m.summary}</p>
            </div>
          )}

          {/* Email Body */}
          <div className="bg-gray-900/50 border border-gray-700 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-purple-400 mb-3">Conteúdo do Email</h3>
            <div className="bg-black/50 border border-gray-600 rounded-lg p-4">
              <pre className="whitespace-pre-wrap text-gray-300 text-sm leading-relaxed font-mono">
                {c.body_text || "(conteúdo vazio)"}
              </pre>
            </div>
          </div>

          {/* Attachments */}
          {attachments.length > 0 && (
            <div className="bg-gray-900/50 border border-gray-700 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-purple-400 mb-3 flex items-center gap-2">
                <Paperclip className="w-5 h-5" />
                Anexos ({attachments.length})
              </h3>
              <div className="space-y-2">
                {attachments.map((a, i) => (
                  <div key={i} className="flex items-center gap-3 p-3 bg-black/50 border border-gray-600 rounded-lg">
                    <Paperclip className="w-4 h-4 text-gray-400" />
                    <div className="flex-1">
                      <p className="text-gray-300 font-medium">{a.filename || "Arquivo sem nome"}</p>
                      <div className="flex gap-4 text-xs text-gray-500">
                        {a.content_type && <span>Tipo: {a.content_type}</span>}
                        {typeof a.size === "number" && <span>Tamanho: {(a.size / 1024).toFixed(1)} KB</span>}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Action Panel */}
          <div className="bg-gray-900/50 border border-gray-700 rounded-lg p-6">
            <ActionPanel emailId={m.id} defaultToEmail="bbitteste@gmail.com" initialDraft={m.reply_suggested || ""} />
          </div>
        </div>
      </div>
    </main>
  )
}
