import csv, os, unicodedata
from typing import List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib

DATA_PATH = "data/examples.csv"
MODEL_DIR = "app/nlp/models"
VEC_PATH = os.path.join(MODEL_DIR, "vectorizer.joblib")
CLF_PATH = os.path.join(MODEL_DIR, "clf.joblib")

def load_csv(path: str) -> Tuple[List[str], List[str]]:
    texts, labels = [], []
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            t = (row.get("text") or "").strip()
            y = (row.get("label") or "").strip()
            if t and y:
                texts.append(t)
                labels.append(y)
    return texts, labels

def strip_accents(s: str) -> str:
    s = s.lower()
    s = unicodedata.normalize("NFD", s)
    return "".join(ch for ch in s if unicodedata.category(ch) != "Mn")

def main():
    os.makedirs(MODEL_DIR, exist_ok=True)

    texts, labels = load_csv(DATA_PATH)
    if not texts:
        raise SystemExit(f"Nenhum dado em {DATA_PATH}. Adicione linhas com 'text,label'.")

    texts_norm = [strip_accents(t) for t in texts]

    X_train, X_test, y_train, y_test = train_test_split(
        texts_norm, labels, test_size=0.25, random_state=42, stratify=labels
    )

    vectorizer = TfidfVectorizer(
        analyzer="word",
        ngram_range=(1, 2),
        min_df=1,
        max_df=0.95,
    )

    Xtr = vectorizer.fit_transform(X_train)
    Xte = vectorizer.transform(X_test)

    clf = LogisticRegression(
        max_iter=2000,
        class_weight="balanced",
        solver="liblinear",
    )
    clf.fit(Xtr, y_train)

    y_pred = clf.predict(Xte)
    acc = accuracy_score(y_test, y_pred)
    print(f"\nAccuracy: {acc:.3f}\n")
    print("Confusion matrix:\n", confusion_matrix(y_test, y_pred))
    print("\nReport:\n", classification_report(y_test, y_pred))

    joblib.dump(vectorizer, VEC_PATH)
    joblib.dump(clf, CLF_PATH)
    print(f"\n✔ Modelo salvo em:\n  {VEC_PATH}\n  {CLF_PATH}\n")

if __name__ == "__main__":
    main()
