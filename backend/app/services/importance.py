import os, re
from datetime import datetime, timezone
from typing import Tuple, List, Dict

def _now() -> datetime:
    return datetime.now(timezone.utc)

def _csv_env(name: str) -> List[str]:
    raw = os.getenv(name, "")
    return [s.strip().lower() for s in raw.split(",") if s.strip()]

URGENCY_PATTERNS = [
    r"\burgent(e)?\b", r"\basap\b", r"\bprioridade\b", r"\bp1\b",
    r"\bprazo\b", r"\bhoje\b", r"\bamanh[ãa]\b", r"\bdeadline\b",
    r"\bultimo\s*dia\b", r"\batrasad[ao]\b",
]

PROD_ATTACH_HINTS = [r"comprovante", r"contrato", r"boleto", r"nf|nota\s*fiscal", r"documento"]

VIP_DOMAINS = set(_csv_env("VIP_DOMAINS"))

def compute_importance(meta: Dict, text: str, category: str) -> Tuple[int, str, List[str]]:
    score = 0
    reasons: List[str] = []

    t = (text or "").lower()
    subject = (meta.get("subject") or "").lower()
    sender = (meta.get("from_email") or "").lower()
    attachments = meta.get("attachments") or []
    received_at = meta.get("received_at")

    vip_list = set(_csv_env("VIP_SENDERS"))
    if sender in vip_list:
        score += 40
        reasons.append("vip_sender")

    domain = sender.split("@")[-1] if "@" in sender else ""
    if domain in VIP_DOMAINS:
        score += 20
        reasons.append("vip_domain")

    urg_hits = [p for p in URGENCY_PATTERNS if re.search(p, t) or re.search(p, subject)]
    if urg_hits:
        score += 20 + 5 * min(3, len(urg_hits))
        reasons.append("urgency_keywords")

    if category == "Produtivo":
        score += 10
        reasons.append("productive")


    attach_names = " ".join([(a.get("filename") or "") for a in attachments]).lower()
    if any(re.search(p, attach_names) for p in PROD_ATTACH_HINTS):
        score += 10
        reasons.append("relevant_attachment")

    if isinstance(received_at, datetime):
        if received_at.tzinfo is None:
            received_at = received_at.replace(tzinfo=timezone.utc)

        age_h = (_now() - received_at).total_seconds() / 3600.0
        if age_h <= 2:
            score += 15; reasons.append("very_recent")
        elif age_h <= 24:
            score += 8; reasons.append("recent")
        elif age_h > 72:
            score -= 5; reasons.append("old")

        hour_utc = received_at.astimezone(timezone.utc).hour
        if 11 <= hour_utc <= 22:
            score += 8; reasons.append("business_hours")
        else:
            score -= 4; reasons.append("off_hours")

    score = max(0, min(100, score))
    if score >= 80:
        label = "urgent"
    elif score >= 50:
        label = "high"
    elif score >= 25:
        label = "normal"
    else:
        label = "low"

    return score, label, reasons[:8]
