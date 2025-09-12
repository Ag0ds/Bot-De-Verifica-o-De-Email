from io import BytesIO
from pdfminer.high_level import extract_text

def extract_text_from_pdf(data: bytes) -> str:
    if not data:
        return ""
    try:
        return extract_text(BytesIO(data)) or ""
    except Exception:
        return ""
