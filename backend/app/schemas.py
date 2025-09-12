from pydantic import BaseModel, Field
from typing import List, Optional

class TranslateRequest(BaseModel):
    subject: Optional[str] = None
    text: Optional[str] = None
    html: Optional[str] = None

class TranslateResponse(BaseModel):
    subject: str
    text: str
    has_pdf_text: bool = False
    length: int

class ProcessResult(BaseModel):
    category: str = Field(..., examples=["Produtivo", "Improdutivo"])
    confidence: float = Field(..., ge=0.0, le=1.0)
    subcategory: Optional[str] = None
    reply: str
    highlights: List[str] = []

class ProcessResponse(BaseModel):
    subject: str
    text: str
    result: ProcessResult
