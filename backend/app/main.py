# app/main.py
import os
from typing import Optional, List

from dotenv import load_dotenv
from fastapi import (
    FastAPI, UploadFile, File, Form, HTTPException, Query, Request, BackgroundTasks
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Tipos leves (mantemos no topo)
from app.schemas import (
    TranslateRequest, TranslateResponse, ProcessResponse,
    GroqSuggestRequest, GroqSuggestResponse,
    SendIntentRequest, SendIntentResponse,
    SendConfirmRequest, SendConfirmResponse,
)

load_dotenv()

app = FastAPI(title="AutoU - Email AI Backend")




origins = [o.strip() for o in os.getenv("FRONTEND_ORIGINS","http://localhost:3000").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- health ----------
@app.get("/health")
def health():
    return {"status": "ok"}

# ---------- helpers ----------
def _mask(email: str) -> str:
    try:
        name, dom = email.split("@", 1)
        if len(name) <= 2:
            return f"{name[0]}***@{dom}"
        return f"{name[:2]}***@{dom}"
    except Exception:
        return "***"

# ---------- translate ----------
@app.post("/api/translate", response_model=TranslateResponse)
def api_translate(payload: TranslateRequest):
    # lazy imports
    from app.pipeline import translate_email

    data = translate_email(
        subject=payload.subject or "",
        body_text=payload.text or "",
        body_html=payload.html or "",
        attachments=[],
    )
    return TranslateResponse(**data)

# ---------- process (upload .pdf/.txt ou texto) ----------
@app.post("/api/process", response_model=ProcessResponse)
async def api_process(
    text: Optional[str] = Form(None),
    subject: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
):
    # lazy imports
    from app.services.pdf_reader import extract_text_from_pdf
    from app.pipeline import process_raw_email

    body_text = text or ""
    body_html = ""
    attachments: List[dict] = []

    if file is not None:
        content = await file.read()
        fname = (file.filename or "").lower()
        ctype = (file.content_type or "").lower()
        if fname.endswith(".pdf") or "pdf" in ctype:
            body_text = extract_text_from_pdf(content)
        elif fname.endswith(".txt"):
            body_text = content.decode(errors="ignore")
        else:
            raise HTTPException(400, detail="Apenas .pdf ou .txt no upload de arquivo.")

    data = process_raw_email(subject or "", body_text, body_html, attachments)
    return ProcessResponse(**data)

# ---------- ingest (só processa e mostra, sem salvar) ----------
@app.get("/api/ingest-from-inbox")
def api_ingest_from_inbox(limit: int = 5):
    # lazy imports
    from app.services.email_ingest import fetch_unread
    from app.pipeline import process_raw_email

    items = []
    for raw in fetch_unread(limit=limit):
        data = process_raw_email(
            subject=raw["subject"],
            body_text=raw["text"],
            body_html=raw["html"],
            attachments=raw["attachments"],
        )
        items.append(data)
    return JSONResponse(content={
        "count": len(items),
        "items": [ProcessResponse(**it).model_dump() for it in items]
    })

# ---------- ingest + salvar no Supabase ----------
@app.post("/api/ingest-and-save")
def api_ingest_and_save(limit: int = 5):
    # lazy imports
    from app.pipeline import translate_email, process_translated_text
    from app.nlp.summarize import summarize
    from app.services.importance import compute_importance
    from app.services.store_email import save_email_pack

    items = []
    from app.services.email_ingest import fetch_unread

    for raw in fetch_unread(limit=limit):
        t = translate_email(raw["subject"], raw["text"], raw["html"], raw["attachments"])
        result = process_translated_text(t["subject"], t["text"])

        summary = summarize(t["text"])
        importance, label, reasons = compute_importance(
            meta={
                "subject": raw["subject"],
                "from_email": raw.get("from_email") or raw.get("from_addr", ""),
                "attachments": raw["attachments"],
                "received_at": raw.get("received_at"),
            },
            text=t["text"],
            category=result.category,
        )

        lite_attachments = [
            {"filename": a.get("filename"), "content_type": a.get("content_type"), "size": a.get("size")}
            for a in raw["attachments"]
        ]

        pack = {
            "message_uid": raw["message_uid"],
            "subject": raw["subject"],
            "from_email": raw.get("from_email") or raw.get("from_addr"),
            "from_name": raw.get("from_name", ""),
            "to_emails": raw.get("to_emails", []),
            "cc_emails": raw.get("cc_emails", []),
            "received_at": raw.get("received_at"),
            "category": result.category,
            "confidence": float(result.confidence),
            "importance": importance,
            "importance_label": label,
            "importance_reasons": reasons,
            "summary": summary,
            "reply_suggested": result.reply,
            "has_pdf": bool(t["has_pdf_text"]),
            "body_text": t["text"],
            "body_html": raw["html"],
            "attachments": lite_attachments,
        }

        email_id = save_email_pack(pack)
        items.append({
            "email_id": email_id,
            "subject": raw["subject"],
            "category": result.category,
            "importance": importance,
            "label": label
        })

    return {"saved": len(items), "items": items}

# ---------- listar/detalhar e-mails do Supabase ----------
@app.get("/api/emails")
def list_emails(
    limit: int = Query(50, ge=1, le=200),
    page: int = Query(1, ge=1),
    importance: str | None = None,   # low|normal|high|urgent
    category: str | None = None,     # Produtivo|Improdutivo
    search: str | None = None,
):
    from app.services.supabase_client import get_supabase

    sb = get_supabase()
    q = sb.table("emails").select("*").order("received_at", desc=True)
    if importance: q = q.eq("importance_label", importance)
    if category:   q = q.eq("category", category)
    if search:     q = q.ilike("subject", f"%{search}%")

    start = (page - 1) * limit
    end = start + limit - 1
    q = q.range(start, end)

    res = q.execute()
    return {"items": res.data or [], "page": page, "limit": limit}

@app.get("/api/emails/{email_id}")
def get_email(email_id: str):
    from app.services.supabase_client import get_supabase
    sb = get_supabase()

    meta = sb.table("emails").select("*").eq("id", email_id).limit(1).execute().data
    meta = meta[0] if meta else None
    if not meta:
        meta2 = sb.table("emails").select("*").eq("message_uid", email_id).limit(1).execute().data
        meta = meta2[0] if meta2 else None

    if not meta:
        raise HTTPException(404, f"email não encontrado: {email_id}")

    real_id = meta["id"]
    content = sb.table("email_contents").select("*").eq("email_id", real_id).limit(1).execute().data
    return {"meta": meta, "content": (content[0] if content else None)}



# ---------- Groq: sugestão de resposta ----------
@app.post("/api/groq/suggest", response_model=GroqSuggestResponse)
def api_groq_suggest(payload: GroqSuggestRequest):
    # lazy imports
    from app.services.supabase_client import get_supabase
    from app.nlp.classify import classify_productive
    from app.services.groq_client import suggest_with_groq

    sb = get_supabase()
    subject = payload.subject or ""
    text = payload.text or ""

    if payload.email_id:
        meta = sb.table("emails").select("subject,id").eq("id", payload.email_id).limit(1).execute().data
        if not meta:
            raise HTTPException(404, "email_id não encontrado")
        subject = subject or meta[0]["subject"] or ""
        content = sb.table("email_contents").select("body_text").eq("email_id", payload.email_id).limit(1).execute().data
        if content and content[0].get("body_text"):
            text = text or content[0]["body_text"]

    if not (subject or text):
        raise HTTPException(400, "forneça email_id ou subject/text")

    category, confidence, _ = classify_productive(text or subject)
    draft = suggest_with_groq(subject, text)
    return GroqSuggestResponse(draft_reply=draft, category=category, confidence=float(confidence))

# ---------- OTP: solicitar envio ----------
@app.post("/api/send-intent", response_model=SendIntentResponse)
def api_send_intent(payload: SendIntentRequest, request: Request):
    # lazy imports
    from app.services.supabase_client import get_supabase
    from app.services.rate_limit import check_email_quota, check_ip_rate
    from app.services.otp import generate_otp, hash_otp
    from app.services.mailer import send_email

    sb = get_supabase()

    # allowed recipient?
    allow = sb.table("allowed_recipients").select("email,is_active").eq("email", payload.to_email.lower()).limit(1).execute().data
    if not allow or not allow[0]["is_active"]:
        raise HTTPException(400, "destinatário não permitido")

    # rate limit
    ip = request.client.host if request and request.client else "0.0.0.0"
    ok_ip, why_ip = check_ip_rate(ip)
    if not ok_ip:
        raise HTTPException(429, f"rate limit IP: {why_ip}")
    ok_em, why_em = check_email_quota(payload.to_email.lower())
    if not ok_em:
        raise HTTPException(429, f"quota de destino: {why_em}")

    meta = sb.table("emails").select("id,subject").eq("id", payload.email_id).limit(1).execute().data
    if not meta:
        raise HTTPException(404, "email_id não encontrado")

    # OTP
    otp = generate_otp()
    otp_hash, salt = hash_otp(otp)
    from datetime import datetime, timedelta, timezone
    ttl_min = int(os.getenv("TOKEN_TTL_MINUTES", "10"))
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=ttl_min)

    token_row = {
        "email_id": payload.email_id,
        "to_email": payload.to_email.lower(),
        "otp_hash": f"{salt}${otp_hash}",
        "expires_at": expires_at.isoformat(),
        "draft_snapshot": (payload.draft or "").strip(),
        "requester_ip": ip,
        "requester_ua": request.headers.get("user-agent", ""),
    }

    ins = sb.table("send_tokens").insert(token_row).execute()
    request_id = None
    if getattr(ins, "data", None):
        try:
            request_id = ins.data[0].get("id")
        except Exception:
            request_id = None
    if not request_id:
        sel = sb.table("send_tokens").select("id").eq("email_id", payload.email_id)\
            .eq("to_email", payload.to_email.lower()).order("created_at", desc=True).limit(1).execute()
        if not sel.data:
            raise HTTPException(500, "falha ao registrar token")
        request_id = sel.data[0]["id"]

    try:
        if os.getenv("DRY_RUN_EMAIL", "").lower() in ("1", "true", "yes"):
            print(f"[DRY_RUN] OTP {otp} para {payload.to_email} (request_id={request_id})")
        else:
            send_email(
                to_email=payload.to_email,
                subject="Código de confirmação (OTP)",
                body=f"Seu código para confirmar o envio é: {otp}\nEste código expira em {ttl_min} minutos.\n\nRef: {request_id}",
            )
    except Exception as e:
        sb.table("send_tokens").update({"status": "blocked"}).eq("id", request_id).execute()
        raise HTTPException(502, f"falha ao enviar OTP: {type(e).__name__}")

    return SendIntentResponse(request_id=request_id, masked_to=_mask(payload.to_email))

@app.post("/api/send-confirm", response_model=SendConfirmResponse)
def api_send_confirm(payload: SendConfirmRequest, background: BackgroundTasks):
    from app.services.supabase_client import get_supabase
    from app.services.otp import verify_otp
    from app.services.mailer import send_email

    sb = get_supabase()

    row = sb.table("send_tokens").select("*").eq("id", payload.request_id).limit(1).execute().data
    if not row:
        raise HTTPException(404, "request_id inválido")
    tok = row[0]

    from datetime import datetime, timezone
    if tok["status"] != "pending":
        raise HTTPException(400, f"status atual: {tok['status']}")
    if datetime.fromisoformat(tok["expires_at"].replace("Z","")).astimezone(timezone.utc) < datetime.now(timezone.utc):
        sb.table("send_tokens").update({"status":"expired"}).eq("id", payload.request_id).execute()
        raise HTTPException(400, "token expirado")

    attempts = int(tok.get("attempts", 0))
    if attempts >= 5:
        sb.table("send_tokens").update({"status":"blocked"}).eq("id", payload.request_id).execute()
        raise HTTPException(400, "muitas tentativas")

    try:
        salt, otp_hash = (tok["otp_hash"] or "").split("$", 1)
    except Exception:
        raise HTTPException(500, "token malformado")
    if not verify_otp(payload.otp, salt, otp_hash):
        sb.table("send_tokens").update({"attempts": attempts+1}).eq("id", payload.request_id).execute()
        raise HTTPException(400, "código inválido")

    sb.table("send_tokens").update({"status":"used"}).eq("id", payload.request_id).execute()

    meta = sb.table("emails").select("subject").eq("id", tok["email_id"]).limit(1).execute().data
    subject = (meta[0]["subject"] if meta else "Resposta")
    draft = tok["draft_snapshot"]
    to_email = tok["to_email"]

    def _do_send():
        import time
        t0 = time.time()
        try:
            provider_id = send_email(to_email, f"RE: {subject}", draft)
            latency = int((time.time() - t0) * 1000)
            sb.table("send_log").insert({
                "email_id": tok["email_id"],
                "to_email": to_email,
                "draft_snapshot": draft,
                "status": "sent",
                "provider_msg_id": provider_id,
                "latency_ms": latency
            }).execute()
        except Exception as e:
            sb.table("send_log").insert({
                "email_id": tok["email_id"],
                "to_email": to_email,
                "draft_snapshot": draft,
                "status": "failed",
                "error": str(e)
            }).execute()

    background.add_task(_do_send)
    return SendConfirmResponse(queued=True)
