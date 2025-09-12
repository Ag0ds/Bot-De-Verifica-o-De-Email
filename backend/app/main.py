from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional, List
from dotenv import load_dotenv
from app.services.store_email import save_email_pack
from app.services.importance import compute_importance
from app.nlp.summarize import summarize
from app.schemas import TranslateRequest, TranslateResponse, ProcessResponse
from app.pipeline import translate_email, process_translated_text, process_raw_email
from app.services.pdf_reader import extract_text_from_pdf
from app.services.email_ingest import fetch_unread
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException, Query
from app.services.supabase_client import get_supabase

load_dotenv()
app = FastAPI(title="AutoU - Email AI Backend")

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/api/translate", response_model=TranslateResponse)
def api_translate(payload: TranslateRequest):
    data = translate_email(
        subject=payload.subject or "",
        body_text=payload.text or "",
        body_html=payload.html or "",
        attachments=[],
    )
    return TranslateResponse(**data)

@app.post("/api/process", response_model=ProcessResponse)
async def api_process(
    text: Optional[str] = Form(None),
    subject: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
):
    body_text = text or ""
    body_html = ""
    attachments: List[dict] = []

    if file is not None:
        content = await file.read()
        if file.filename.lower().endswith(".pdf") or "pdf" in (file.content_type or "").lower():
            body_text = extract_text_from_pdf(content)
        elif file.filename.lower().endswith(".txt"):
            body_text = content.decode(errors="ignore")
        else:
            raise HTTPException(400, detail="Apenas .pdf ou .txt no upload de arquivo.")

    data = process_raw_email(subject or "", body_text, body_html, attachments)
    return ProcessResponse(**data)

@app.get("/api/ingest-from-inbox")
def api_ingest_from_inbox(limit: int = 5):
    items = []
    for raw in fetch_unread(limit=limit):
        data = process_raw_email(
            subject=raw["subject"],
            body_text=raw["text"],
            body_html=raw["html"],
            attachments=raw["attachments"],
        )
        items.append(data)
    return JSONResponse(content={"count": len(items), "items": [ProcessResponse(**it).model_dump() for it in items]})

@app.post("/api/ingest-and-save")
def api_ingest_and_save(limit: int = 5):
    items = []
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
        items.append({"email_id": email_id, "subject": raw["subject"], "category": result.category, "importance": importance, "label": label})

    return {"saved": len(items), "items": items}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/emails")
def list_emails(
    limit: int = Query(50, ge=1, le=200),
    page: int = Query(1, ge=1),
    importance: str | None = None,   
    category: str | None = None,   
    search: str | None = None,
):
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
    sb = get_supabase()
    meta = sb.table("emails").select("*").eq("id", email_id).limit(1).execute().data
    if not meta:
        raise HTTPException(404, "email não encontrado")
    content = sb.table("email_contents").select("*").eq("email_id", email_id).limit(1).execute().data
    return {"meta": meta[0], "content": (content[0] if content else None)}