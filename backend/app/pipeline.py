from typing import List, Dict
from app.schemas import ProcessResult
from app.nlp.preprocess import html_to_text, clean_email_text
from app.services.pdf_reader import extract_text_from_pdf
from app.nlp.classify import classify_productive
from app.nlp.reply import suggest_reply

def translate_email(subject: str, body_text: str, body_html: str, attachments: List[Dict]) -> dict:
    if body_text and body_text.strip():
        base = body_text
    else:
        base = html_to_text(body_html)

    base_clean = clean_email_text(base)

    pdf_texts: List[str] = []
    for att in attachments or []:
        ctype = (att.get("content_type") or "").lower()
        fname = (att.get("filename") or "").lower()
        if "pdf" in ctype or fname.endswith(".pdf"):
            t = extract_text_from_pdf(att.get("content") or b"")
            t = clean_email_text(t)
            if t:
                pdf_texts.append(t)

    if not base_clean or len(base_clean) < 40:
        final_text = " ".join([s for s in [base_clean] + pdf_texts if s])
    else:
        if pdf_texts:
            final_text = base_clean + "\n\n--- Texto extraído de anexos PDF ---\n" + "\n\n".join(pdf_texts)
        else:
            final_text = base_clean

    return {
        "subject": (subject or "").strip(),
        "text": (final_text or "").strip(),
        "has_pdf_text": len(pdf_texts) > 0,
        "length": len(final_text or ""),
    }

def process_translated_text(subject: str, text: str) -> ProcessResult:
    category, confidence, highlights = classify_productive(text)
    reply = suggest_reply(category, text)
    return ProcessResult(
        category=category,
        confidence=round(confidence, 2),
        subcategory=None,
        reply=reply,
        highlights=highlights,
    )

def process_raw_email(subject: str, body_text: str, body_html: str, attachments: List[Dict]) -> dict:
    t = translate_email(subject, body_text, body_html, attachments)
    result = process_translated_text(t["subject"], t["text"])
    return {
        "subject": t["subject"],
        "text": t["text"],
        "result": result,
    }

def process_email_payload(subject: str, body_text: str, body_html: str = "") -> ProcessResult:
    t = translate_email(subject, body_text, body_html, attachments=[])
    return process_translated_text(t["subject"], t["text"])
