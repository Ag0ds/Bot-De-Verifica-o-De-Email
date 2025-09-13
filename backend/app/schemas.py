from pydantic import BaseModel, Field, EmailStr
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

class GroqSuggestRequest(BaseModel):
    email_id: Optional[str] = None
    subject: Optional[str] = None
    text: Optional[str] = None

class GroqSuggestResponse(BaseModel):
    draft_reply: str
    category: str
    confidence: float

class SendIntentRequest(BaseModel):
    email_id: str
    to_email: EmailStr
    draft: str

class SendIntentResponse(BaseModel):
    request_id: str
    masked_to: str

class SendConfirmRequest(BaseModel):
    request_id: str
    otp: str

class SendConfirmResponse(BaseModel):
    queued: bool = True
