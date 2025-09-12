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
            yield {
                "subject": msg.subject or "",
                "text": msg.text or "",
                "html": msg.html or "",
                "attachments": atts,
            }
