import os
from typing import Generator, Dict, Any, List
from imap_tools import MailBox, A

def fetch_unread(limit: int = 10) -> Generator[Dict[str, Any], None, None]:
    host    = os.getenv("IMAP_HOST", "imap.gmail.com")
    user    = os.getenv("IMAP_USER")
    passwd  = os.getenv("IMAP_PASS")
    folder  = os.getenv("IMAP_FOLDER", "INBOX")

    if not (host and user and passwd):
        raise RuntimeError("IMAP_HOST/IMAP_USER/IMAP_PASS não configurados (.env).")

    with MailBox(host).login(user, passwd, folder) as mailbox:
        for msg in mailbox.fetch(A(seen=False), limit=limit, reverse=True):
            atts: List[Dict[str, Any]] = []
            for att in getattr(msg, "attachments", []):
                atts.append({
                    "filename": att.filename,
                    "content": att.payload,        
                    "content_type": (att.content_type or ""),
                    "size": (att.size or 0),
                })
            from_addr = (msg.from_ or "")
            from_name = ""
            from_email = ""
            try:
                if msg.from_values:  # list[Address]
                    from_name = msg.from_values[0].name or ""
                    from_email = msg.from_values[0].email or ""
            except Exception:
                pass

            to_emails = []
            try:
                to_emails = [a.email for a in (msg.to_values or []) if getattr(a, "email", None)]
            except Exception:
                pass

            cc_emails = []
            try:
                cc_emails = [a.email for a in (msg.cc_values or []) if getattr(a, "email", None)]
            except Exception:
                pass

            yield {
                "message_uid": str(msg.uid) if getattr(msg, "uid", None) is not None else (msg.message_id or ""),
                "subject": msg.subject or "",
                "text": msg.text or "",
                "html": msg.html or "",
                "attachments": atts,          # [{filename, content(bytes), content_type, size}]

                # novos metadados
                "from_addr": from_addr,
                "from_name": from_name,
                "from_email": from_email or from_addr,
                "to_emails": to_emails,
                "cc_emails": cc_emails,
                "received_at": msg.date,      # datetime
            }
