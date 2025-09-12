from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional, List
from dotenv import load_dotenv

from app.schemas import TranslateRequest, TranslateResponse, ProcessResponse
from app.pipeline import translate_email, process_translated_text, process_raw_email
from app.services.pdf_reader import extract_text_from_pdf
from app.services.email_ingest import fetch_unread

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
