from __future__ import annotations
import re
import unicodedata
from typing import List, Optional, Tuple

# Palavras/expressões que costumam indicar conteúdo útil
KEYWORDS = [
    # produtivo
    "status", "protocolo", "ticket", "chamado", "andamento", "prazo",
    "anexo", "comprovante", "arquivo", "documento", "contrato",
    "erro", "falha", "indisponibilidade", "acesso", "senha", "bloqueio",
    "fatura", "boleto", "pagamento", "nota fiscal", "nf",
    "pedido", "solicitacao", "solicitação", "requisicao", "requisição",
    # urgência
    "urgente", "asap", "prioridade", "p1", "deadline", "hoje", "amanha", "amanhã",
    "ultimo dia", "atrasado", "atrasada",
]

_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")
_WS = re.compile(r"\s+")
_PUNCT = re.compile(r"[^\w\s]")

def _norm(s: str) -> str:
    s = s.lower()
    s = unicodedata.normalize("NFD", s)
    return "".join(ch for ch in s if unicodedata.category(ch) != "Mn")

def _split_sentences(t: str) -> List[str]:
    t = (t or "").strip()
    if not t:
        return []
    parts = _SENT_SPLIT.split(t)
    cleaned = []
    for p in parts:
        p = _WS.sub(" ", p).strip()
        if len(p) < 3:
            continue
        cleaned.append(p)
    return cleaned

def _overlap(a: str, b: str) -> float:
    ta = set(_WS.split(_norm(a)))
    tb = set(_WS.split(_norm(b)))
    if not ta or not tb:
        return 0.0
    inter = len(ta & tb)
    union = len(ta | tb)
    return inter / union

def _score_sentence(sent: str, idx: int, subject_norm: str) -> float:
    s_norm = _norm(sent)
    score = 0.0

    # keywords
    kw_hits = sum(1 for k in KEYWORDS if k in s_norm)
    score += 2.0 * kw_hits

    # posição (primeiras frases tendem a carregar contexto)
    score += max(0.0, 1.5 - 0.15 * idx)

    # match com assunto
    if subject_norm:
        # interseção de tokens (rápido e robusto)
        sa = set(_WS.split(subject_norm))
        ss = set(_WS.split(s_norm))
        score += 0.8 * len(sa & ss)

    # tamanho: ideal entre 40 e 220 chars
    n = len(sent)
    if n < 30:
        score -= 0.3
    elif n > 260:
        score -= 0.4

    return score

def summarize(text: str, max_chars: int = 280, subject: Optional[str] = None) -> str:
    if not text:
        return ""

    sentences = _split_sentences(text)
    if not sentences:
        # fallback: texto unico, normaliza e corta
        s = _WS.sub(" ", text).strip()
        return (s[: max_chars - 1] + "…") if len(s) > max_chars else s

    subj_norm = _norm(subject or "")

    # pontua todas as sentenças
    scored: List[Tuple[float, int, str]] = []
    for i, s in enumerate(sentences):
        scored.append((_score_sentence(s, i, subj_norm), i, s))

    # ordena por score desc, mantendo estabilidade por índice
    scored.sort(key=lambda x: (-x[0], x[1]))

    # escolhe a melhor e tenta adicionar uma segunda com baixa sobreposição
    chosen: List[str] = []
    if scored:
        chosen.append(scored[0][2])

    for _, _, cand in scored[1:]:
        if len(chosen) >= 2:
            break
        if _overlap(chosen[0], cand) < 0.5:
            chosen.append(cand)

    # monta o resumo
    summary = " ".join(chosen).strip()
    summary = _WS.sub(" ", summary)

    # corta no limite
    if len(summary) > max_chars:
        summary = summary[: max_chars - 1].rstrip() + "…"

    return summary

__all__ = ["summarize"]
