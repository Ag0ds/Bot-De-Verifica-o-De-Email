import re

def summarize(text: str, max_chars: int = 280) -> str:
    t = (text or "").strip()
    if not t:
        return ""
    parts = re.split(r"(?<=[.!?])\s+", t)
    summary = " ".join(parts[:2]).strip()
    summary = re.sub(r"\s+", " ", summary)
    if len(summary) > max_chars:
        summary = summary[:max_chars - 1].rstrip() + "…"
    return summary
