import os
import unicodedata
from typing import Tuple, List

try:
    import joblib  # type: ignore
except Exception:
    joblib = None  # tipo: ignore


MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
VEC_PATH = os.path.join(MODEL_DIR, "vectorizer.joblib")
CLF_PATH = os.path.join(MODEL_DIR, "clf.joblib")

VECTORIZER = None
CLF = None
IDX_CLASS = {}

def _strip_accents(s: str) -> str:
    s = s.lower()
    s = unicodedata.normalize("NFD", s)
    return "".join(ch for ch in s if unicodedata.category(ch) != "Mn")

def _load_model():
    global VECTORIZER, CLF, IDX_CLASS
    if VECTORIZER is not None and CLF is not None:
        return
    if joblib and os.path.exists(VEC_PATH) and os.path.exists(CLF_PATH):
        VECTORIZER = joblib.load(VEC_PATH)
        CLF = joblib.load(CLF_PATH)
        IDX_CLASS = {c: i for i, c in enumerate(list(CLF.classes_))}


PRODUTIVO_HINTS = [
    "status", "protocolo", "andamento", "suporte", "erro",
    "anexo", "comprovante", "prazo", "ticket", "requisicao", "solicitação",
]
IMPRODUTIVO_HINTS = [
    "feliz natal", "parabéns", "obrigado", "agradeço", "bom dia", "boa tarde", "boa noite", "ok", "ciente"
]

def _heuristic(text: str) -> Tuple[str, float, List[str]]:
    t = (text or "").lower()
    hits_prod = [w for w in PRODUTIVO_HINTS if w in t]
    hits_improd = [w for w in IMPRODUTIVO_HINTS if w in t]

    if hits_prod and not hits_improd:
        return "Produtivo", min(0.5 + 0.1 * len(hits_prod), 0.95), hits_prod[:6]
    if hits_improd and not hits_prod:
        return "Improdutivo", min(0.5 + 0.1 * len(hits_improd), 0.95), hits_improd[:6]

    if "?" in t or "favor" in t or "poderiam" in t or "pode verificar" in t:
        return "Produtivo", 0.6, []
    return "Improdutivo", 0.6, []


def classify_productive(text: str) -> Tuple[str, float, List[str]]:
    _load_model()
    if VECTORIZER is None or CLF is None:
        return _heuristic(text)

    t = _strip_accents(text or "")
    X = VECTORIZER.transform([t])
    proba = CLF.predict_proba(X)[0]
    classes = list(CLF.classes_)

    idx_prod = IDX_CLASS.get("Produtivo")
    idx_impr = IDX_CLASS.get("Improdutivo")
    if idx_prod is None or idx_impr is None:
        return _heuristic(text)

    p_prod = float(proba[idx_prod])
    p_impr = float(proba[idx_impr])

    if p_prod >= p_impr:
        category, confidence = "Produtivo", p_prod
    else:
        category, confidence = "Improdutivo", p_impr

    highlights: List[str] = []
    try:
        feats = getattr(VECTORIZER, "get_feature_names_out")()
        present_idxs = X.nonzero()[1].tolist()
        for idx in present_idxs[:15]:
            term = feats[idx]
            if len(term) >= 3:
                highlights.append(term)
    except Exception:
        pass

    return category, round(confidence, 2), highlights[:6]
