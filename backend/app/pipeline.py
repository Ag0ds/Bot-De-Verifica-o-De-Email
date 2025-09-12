from typing import List, Dict
from app.nlp.preprocess import html_to_text, clean_email_text
from app.services.pdf_reader import extract_text_from_pdf

def translate_email(subject: str, body_text: str, body_html: str, attachments: List[Dict]) -> dict:
    if body_text and body_text.strip():
        base = body_text
    else:
        base = html_to_text(body_html)

    base_clean = clean_email_text(base)
    pdf_texts = []
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
        "text": final_text.strip(),
        "has_pdf_text": len(pdf_texts) > 0,
        "length": len(final_text or ""),
    }
