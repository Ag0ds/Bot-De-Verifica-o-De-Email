import Link from "next/link"
import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Mail, Brain, Sparkles, RefreshCw } from "lucide-react"
import RefreshButton from "@/components/RefreshButton";


const API_BASE = (process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8000").replace(/\/$/, "");

type EmailItem = {
  id?: string
  email_id?: string
  message_uid?: string
  subject: string
  category?: string
  importance_label?: string
  summary?: string
  received_at?: string
}

type ListResp = { items: EmailItem[]; page: number; limit: number }

function resolveOpenId(m: EmailItem): string {
  return m.id ?? m.message_uid ?? m.email_id ?? ""
}

function getCategoryColor(category?: string) {
  if (!category) return "bg-muted text-muted-foreground"

  switch (category.toLowerCase()) {
    case "produtivo":
    case "productive":
      return "bg-green-500/20 text-green-400 border-green-500/30"
    case "improdutivo":
    case "unproductive":
      return "bg-red-500/20 text-red-400 border-red-500/30"
    default:
      return "bg-primary/20 text-primary border-primary/30"
  }
}

function getImportanceColor(importance?: string) {
  if (!importance) return "bg-muted text-muted-foreground"

  switch (importance.toLowerCase()) {
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
      return "bg-accent/20 text-accent-foreground border-accent/30"
  }
}

export const dynamic = 'force-dynamic';
export const revalidate = 0;

export default async function Page() {
  let data: ListResp | null = null;
  let error = false;

  try {
    const url = `${API_BASE}/api/emails?limit=50`;
    const res = await fetch(url, { cache: "no-store" });
    if (res.ok) {
      data = await res.json();
    } else {
      console.error("GET", url, "->", res.status, await res.text());
      error = true;
    }
  } catch (e) {
    console.error(e);
    error = true;
  }

  const items: EmailItem[] = Array.isArray(data?.items) ? data.items : []

  return (
    <div className="min-h-screen bg-background">
      <header className="neon-line border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-primary/20 border border-primary/30">
                <Brain className="h-6 w-6 text-primary" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-foreground">AI Email Analyzer</h1>
                <p className="text-sm text-muted-foreground">Análise inteligente de emails</p>
              </div>
            </div>
            <Button variant="outline" size="sm" asChild>
              <RefreshButton runIngest />
            </Button>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card className="bg-card border-border">
            <CardContent className="p-6">
              <div className="flex items-center gap-3">
                <Mail className="h-8 w-8 text-primary" />
                <div>
                  <p className="text-2xl font-bold text-foreground">{items.length}</p>
                  <p className="text-sm text-muted-foreground">Total de Emails</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-card border-border">
            <CardContent className="p-6">
              <div className="flex items-center gap-3">
                <Sparkles className="h-8 w-8 text-green-400" />
                <div>
                  <p className="text-2xl font-bold text-foreground">
                    {items.filter((item) => item.category?.toLowerCase().includes("produtiv")).length}
                  </p>
                  <p className="text-sm text-muted-foreground">Produtivos</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-card border-border">
            <CardContent className="p-6">
              <div className="flex items-center gap-3">
                <div className="h-8 w-8 rounded-full bg-red-500/20 flex items-center justify-center">
                  <div className="h-4 w-4 rounded-full bg-red-400"></div>
                </div>
                <div>
                  <p className="text-2xl font-bold text-foreground">
                    {items.filter((item) => item.category?.toLowerCase().includes("improdutiv")).length}
                  </p>
                  <p className="text-sm text-muted-foreground">Improdutivos</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {error && (
          <Card className="bg-red-950/50 border-red-800/50">
            <CardContent className="p-6">
              <p className="text-red-200 font-medium">Falha ao carregar a lista de emails.</p>
            </CardContent>
          </Card>
        )}

        {!error && items.length === 0 && (
          <Card className="bg-card border-border">
            <CardContent className="p-12 text-center">
              <Mail className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-lg text-muted-foreground">Nenhum email encontrado.</p>
              <p className="text-sm text-muted-foreground mt-2">Conecte sua conta de email para começar a análise.</p>
            </CardContent>
          </Card>
        )}

        {items.length > 0 && (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-foreground mb-4">Emails Analisados</h2>
            {items.map((email: EmailItem) => {
              const openId = resolveOpenId(email)
              return (
                <Card
                  key={openId || email.subject}
                  className="bg-card border-border hover:bg-card/80 transition-colors"
                >
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between gap-4">
                      <h3 className="font-semibold text-foreground text-balance leading-tight truncate max-w-[70%]">
                        {email.subject || "(sem assunto)"}
                      </h3>
                      <div className="flex gap-2 flex-shrink-0">
                        {email.category && (
                          <Badge variant="outline" className={getCategoryColor(email.category)}>
                            {email.category}
                          </Badge>
                        )}
                        {email.importance_label && (
                          <Badge variant="outline" className={getImportanceColor(email.importance_label)}>
                            {email.importance_label}
                          </Badge>
                        )}
                      </div>
                    </div>
                  </CardHeader>

                  <CardContent className="pt-0">
                    {email.summary && (
                      <p className="text-muted-foreground text-sm mb-4 text-pretty leading-relaxed line-clamp-3">
                        {email.summary}
                      </p>
                    )}

                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        {openId ? (
                          <Button variant="default" size="sm" asChild>
                            <Link href={`/email/${encodeURIComponent(openId)}`}>Abrir Email</Link>
                          </Button>
                        ) : (
                          <Button variant="outline" size="sm" disabled>
                            Sem ID disponível
                          </Button>
                        )}
                      </div>

                      <div className="text-xs text-muted-foreground font-mono truncate max-w-[40%]">
                        ID: {email.id ?? "—"} | UID: {email.message_uid ?? "—"}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        )}
      </main>
    </div>
  )
}
