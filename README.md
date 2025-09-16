# Bot de Verificação de Email
> **Case Prático – AutoU**
> Classificação automática de emails (Produtivo/Improdutivo), resumo, sugestão de resposta com
LLM, priorização por importância e fluxo seguro de envio com OTP.
---
## Sumário
- [Visão Geral](#visão-geral)
- [Principais Funcionalidades](#principais-funcionalidades)
- [Arquitetura](#arquitetura)
- [Stack Técnica](#stack-técnica)
- [Estrutura do Repositório](#estrutura-do-repositório)
- [Backend](#backend)
 - [Variáveis de Ambiente (.env)](#variáveis-de-ambiente-env)
 - [Instalação e Execução Local](#instalação-e-execução-local)
 - [Endpoints](#endpoints)
- [Supabase – Esquema de Banco](#supabase--esquema-de-banco)
- [Cron (opcional)](#cron-opcional)
- [Frontend](#frontend)
- [Licença](#licença)
---
## Visão Geral
O projeto automatiza o fluxo de leitura de emails de uma caixa IMAP, classifica o teor
(Produtivo/Improdutivo), gera **resumo** e **sugere respostas** com um LLM (Groq). Cada email
recebe um **score de importância** (urgência, remetente VIP, anexos relevantes e recência). A
interface web permite revisar a lista, abrir o detalhe e **enviar a resposta** com um fluxo
seguro de **OTP** (one-time password) e **lista de destinatários permitidos**.
---
## Principais Funcionalidades
- **Ingestão via IMAP** (emails não lidos; PDF/TXT extraído para texto).
- **Classificação** (baseline local com Scikit-Learn): *Produtivo* vs *Improdutivo*.
- **Resumo** do corpo (heurística leve).
- **Importância**: urgência (palavras), VIP, anexos, recência → *urgent/high/normal/low*.
- **Sugestão de resposta** com **Groq** (LLM).
- **Envio seguro**:
 - `allowed_recipients` (lista de destinatários permitidos)
 - **OTP** por email (TTL curto) e **rate-limit** (IP/destinatário)
- **Persistência** no **Supabase** (metadados, corpo, tokens e logs).
- **Frontend (Next.js)** com listagem, filtros e fluxo de envio.
---
## Arquitetura
```
          +-------------+         +--------------------+
IMAP ---> | Ingestão    | ----->  | Pipeline NLP       |
          | (imap-tools)|         | - limpeza/TF-IDF   |
          +------+------+         | - classificação     |
                 |                | - resumo            |
                 v                +---------+----------+
         +-------+---------+                |
         | Persistência    | (Supabase) <---+
         | emails, contents, tokens, logs   |
         +-------+---------+                |
                 ^                          v
                 |                  +-------+--------+
                 +------------------+ Sugestão LLM   |
                                    | (Groq)         |
                                    +-------+--------+
                                            |
                                            v
                                     Frontend (Next.js)
```
---
## Stack Técnica
- **Backend:** FastAPI, Uvicorn, Python 3.12, Docker
- **NLP:** Scikit-Learn (TF-IDF + Logistic Regression/SVM), NLTK, pdfminer.six
- **Emails:** imap-tools (IMAP), SMTP padrão (envio OTP/respostas)
- **LLM:** Groq API (chat.completions)
- **Banco:** Supabase (PostgreSQL + PostgREST)
- **Frontend:** Next.js (App Router), Vercel
- **Infra opcional:** GitHub Actions/Render Cron para agendamento
---
## Estrutura do Repositório
## Estrutura do Repositório
```
/
  backend/
    app/
      main.py
      pipeline.py
      schemas.py
      nlp/
        classify.py
        reply.py
        summarize.py
      services/
        email_ingest.py
        pdf_reader.py
        importance.py
        store_email.py
        supabase_client.py
        groq_client.py
        otp.py
        rate_limit.py
        mailer.py
    scripts/
      ingest_save_supabase.py
      train_baseline.py
      purge_imap.py
      purge_supabase.py
    requirements.txt
    Dockerfile
    .dockerignore
    .env.example
  frontend/
    app/
      page.tsx
      email/[id]/page.tsx
    ... (componentes e config)
  README.md
```
---
## Backend
### Variáveis de Ambiente (.env)
Crie `backend/.env` a partir de `.env.example`:
```env
# === Supabase ===
SUPABASE_URL=https://SEU_PROJETO.supabase.co
SUPABASE_SERVICE_ROLE_KEY=SEU_SERVICE_ROLE
# === IMAP (ingestão) ===
IMAP_HOST=imap.gmail.com
IMAP_USER=seu.email@gmail.com
IMAP_PASS=SENHA_DE_APP
IMAP_FOLDER=INBOX
IMAP_TRASH_FOLDER=[Gmail]/Trash
# === SMTP (envio OTP e respostas) ===
SMTP_HOST=smtp.seuprovedor.com
SMTP_PORT=587
SMTP_USER=usuario
SMTP_PASS=senha
SENDER_EMAIL=no-reply@suaempresa.com
SENDER_NAME=AutoU Bot
# === LLM (Groq) ===
GROQ_API_KEY=grq_xxxxxxxxxxxxxxxxx
# === Backend ===
TOKEN_TTL_MINUTES=10
DRY_RUN_EMAIL=false
FRONTEND_ORIGINS=http://localhost:3000
# === VIPs/urgência (opcional) ===
VIP_SENDERS=cliente@vip.com, diretor@empresa.com
VIP_DOMAINS=parceiro.com,empresa.com.br
```
> **Segurança:** nunca exponha `SERVICE_ROLE_KEY` no frontend.
### Instalação e Execução Local
```bash
cd backend
python -m venv .venv
. .venv/Scripts/activate # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
# rodar API
set PYTHONPATH=%cd% # (Windows) / export PYTHONPATH=$PWD (bash)
uvicorn app.main:app --reload --port 8000
# http://127.0.0.1:8000/health -> {"status":"ok"}
```
#### (Opcional) Treinar o classificador baseline
```bash
python -m scripts.train_baseline
```
#### Ingestão manual e teste
```bash
# lê IMAP, processa e salva no Supabase
curl -X POST "http://127.0.0.1:8000/api/ingest-and-save?limit=10"
# lista
curl "http://127.0.0.1:8000/api/emails?limit=5"
```
### Endpoints
- `GET /health` → status
- `POST /api/translate` → normaliza/extrai texto (PDF/TXT), saída canônica
- `POST /api/process` → classificação + resumo (input: texto/arquivo)
- `GET /api/ingest-from-inbox?limit=5` → ingestão em memória (sem persistir)
- `POST /api/ingest-and-save?limit=5` → ingestão + persistência no Supabase
- `GET /api/emails?limit=&page=&importance=&category=&search=` → lista paginada
- `GET /api/emails/{email_id}` → detalhe (meta + conteúdo)
- `POST /api/groq/suggest` → `{"subject","text"}` ou `{"email_id"}` → rascunho
- `POST /api/send-intent` → `{ email_id, to_email, draft }` → envia **OTP**
- `POST /api/send-confirm` → `{ request_id, otp }` → envia email final e loga
---
## Supabase – Esquema de Banco
> Execute no SQL editor do Supabase (ajuste tipos se necessário).
```sql
-- emails (metadados)
create table if not exists emails (
 id uuid primary key default gen_random_uuid(),
 message_uid text,
 subject text,
 from_email text,
 from_name text,
 to_emails text[] default '{}',
 cc_emails text[] default '{}',
 received_at timestamptz,
 category text,
 confidence double precision,
 importance int,
 importance_label text,
 importance_reasons text[] default '{}',
 summary text,
 reply_suggested text,
 has_pdf boolean default false,
 created_at timestamptz default now()
);
-- conteúdo (corpo)
create table if not exists email_contents (
 email_id uuid references emails(id) on delete cascade,
 body_text text,
 body_html text,
 attachments jsonb default '[]',
 primary key (email_id)
);
-- lista branca de destinatários
create table if not exists allowed_recipients (
 email text primary key,
 display_name text,
 is_active boolean default true
);
-- tokens (OTP) para envio
create table if not exists send_tokens (
 id uuid primary key default gen_random_uuid(),
 email_id uuid references emails(id) on delete cascade,
 to_email text not null,
 otp_hash text not null, -- "salt$hash"
 expires_at timestamptz not null,
 attempts int default 0,
 status text default 'pending', -- pending|used|expired|blocked
 draft_snapshot text, -- congelar rascunho aprovado
 requester_ip text,
 requester_ua text,
 created_at timestamptz default now()
);
-- logs de envio
create table if not exists send_log (
 id uuid primary key default gen_random_uuid(),
 email_id uuid references emails(id) on delete set null,
 to_email text,
 draft_snapshot text,
 status text, -- sent|failed
 provider_msg_id text,
 latency_ms int,
 error text,
 created_at timestamptz default now()
);
```
> **RLS**: pode ser habilitado conforme necessidade. O backend usa **Service Role**.
---
## Cron (opcional)
### GitHub Actions (agendamento a cada 30 min)
`.github/workflows/ingest.yml`
```yaml
name: Ingest Emails (cron)
on:
 schedule:
 - cron: "*/30 * * * *"
 workflow_dispatch: {}
jobs:
 ingest:
 runs-on: ubuntu-latest
 defaults: { run: { working-directory: backend } }
 steps:
 - uses: actions/checkout@v4
 - uses: actions/setup-python@v5
 with:
 python-version: "3.12"
 cache: "pip"
 cache-dependency-path: backend/requirements.txt
 - run: pip install -r requirements.txt
 - name: Run ingestion
 env:
 IMAP_HOST: ${{ secrets.IMAP_HOST }}
 IMAP_USER: ${{ secrets.IMAP_USER }}
 IMAP_PASS: ${{ secrets.IMAP_PASS }}
 IMAP_FOLDER: ${{ secrets.IMAP_FOLDER }}
 SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
 SUPABASE_SERVICE_ROLE_KEY: ${{ secrets.SUPABASE_SERVICE_ROLE_KEY }}
 PYTHONPATH: .
 run: python -m scripts.ingest_save_supabase
```
---
## Frontend
### Variáveis de Ambiente
Crie `frontend/.env.local`:
```env
NEXT_PUBLIC_API_BASE=http://127.0.0.1:8000
```
> Em produção, aponte para o Render:
> `NEXT_PUBLIC_API_BASE=https://SEU-BACKEND.onrender.com`
### Execução
```bash
cd frontend
npm install
npm run dev
# http://localhost:3000
```
> Em páginas que listam dados, use:
```ts
export const dynamic = 'force-dynamic';
export const revalidate = 0;
```
---
## Licença
[MIT](./LICENSE)
