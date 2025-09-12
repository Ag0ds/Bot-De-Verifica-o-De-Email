from typing import Dict, Any
from datetime import datetime, timezone
from app.services.supabase_client import get_supabase

def _iso(dt):
    if isinstance(dt, datetime):
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()
    return dt

def save_email_pack(pack: Dict[str, Any]) -> str:
    sb = get_supabase()

    meta = {
        "message_uid": pack.get("message_uid"),
        "subject": pack.get("subject"),
        "from_email": pack.get("from_email"),
        "from_name": pack.get("from_name"),
        "to_emails": pack.get("to_emails"),
        "cc_emails": pack.get("cc_emails"),
        "received_at": _iso(pack.get("received_at")),
        "category": pack.get("category"),
        "confidence": pack.get("confidence"),
        "importance": pack.get("importance"),
        "importance_label": pack.get("importance_label"),
        "importance_reasons": pack.get("importance_reasons"),
        "summary": pack.get("summary"),
        "reply_suggested": pack.get("reply_suggested"),
        "has_pdf": pack.get("has_pdf"),
    }

    if not meta["message_uid"]:
        raise RuntimeError("message_uid ausente no pack — precisa ser único para upsert.")
    up = sb.table("emails").upsert(meta, on_conflict="message_uid").execute()

    email_id = None
    if getattr(up, "data", None):
        row0 = up.data[0]
        email_id = row0.get("id")
    if not email_id:
        sel = sb.table("emails").select("id").eq("message_uid", meta["message_uid"]).limit(1).execute()
        if not sel.data:
            raise RuntimeError(f"Upsert OK, mas não consegui buscar id de message_uid={meta['message_uid']}")
        email_id = sel.data[0]["id"]

    contents = {
        "email_id": email_id,
        "body_text": pack.get("body_text"),
        "body_html": pack.get("body_html"),
        "attachments": pack.get("attachments"),
    }
    sb.table("email_contents").upsert(contents, on_conflict="email_id").execute()
    return email_id
