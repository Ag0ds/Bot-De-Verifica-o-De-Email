from dotenv import load_dotenv
from app.services.email_ingest import fetch_unread
from app.pipeline import translate_email, process_translated_text
from app.nlp.summarize import summarize
from app.services.importance import compute_importance
from app.services.store_email import save_email_pack

def main():
    load_dotenv()
    count = 0
    for raw in fetch_unread(limit=10):
        t = translate_email(
            subject=raw["subject"],
            body_text=raw["text"],
            body_html=raw["html"],
            attachments=raw["attachments"],
        )
        result = process_translated_text(t["subject"], t["text"])

        summary = summarize(t["text"])
        importance, label, reasons = compute_importance(
            meta={
                "subject": raw["subject"],
                "from_email": raw["from_email"] if "from_email" in raw else raw.get("from_addr",""),
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
        print(f"✔ salvo email_id={email_id} | {result.category}/{label} | {raw['subject'][:60]}")
        count += 1

    print(f"\nTotal salvos: {count}")

if __name__ == "__main__":
    main()
