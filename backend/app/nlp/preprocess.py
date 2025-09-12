import re
from bs4 import BeautifulSoup

def html_to_text(html: str) -> str:
    if not html:
        return ""
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style"]):
        tag.extract()
    text = soup.get_text(separator=" ")
    return text

def strip_quoted_replies(text: str) -> str:
    if not text:
        return ""
    patterns = [
        r"On .* wrote:.*",            # EN
        r"Em .* escreveu:.*",         # PT
        r"-----Original Message-----",# EN/Outlook
        r"De: .*",                    # PT
    ]
    for p in patterns:
        text = re.sub(p, "", text, flags=re.IGNORECASE | re.DOTALL)
    return text

def normalize_whitespace(text: str) -> str:
    if not text:
        return ""
    text = text.replace("\r", " ").replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def clean_email_text(raw: str) -> str:
    t = raw or ""
    t = strip_quoted_replies(t)
    t = normalize_whitespace(t)
    return t[:20000]
