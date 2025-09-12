# AutoU — Email Classification Bot

> 🇧🇷 **Este README está em Português e Inglês.**
> 🇺🇸 **This README is provided in Portuguese and English.**

---

[Leia em Português](#-pt-br) | [Read in English](#-en-us)

---

## 🇧🇷 PT-BR

### Visão Geral
Aplicação web simples que **classifica e-mails** em **Produtivo** ou **Improdutivo** e **sugere uma resposta automática** apropriada. O objetivo é **reduzir trabalho manual** de triagem, mantendo **clareza**, **rapidez** e **boa experiência de uso**.

### Principais Recursos
- **Upload** de `.txt`/`.pdf` ou **colar texto** direto na página.
- **Pré-processamento** de linguagem (lowercase, remoção de stopwords PT-BR, stemming/lematização).
- **Classificação** (Produtivo × Improdutivo):
  - *Baseline local* (TF-IDF + Logistic Regression, sem GPU/externo), **ou**
  - *Zero-shot* opcional via Hugging Face / OpenAI (qualidade superior).
- **Resposta sugerida** com **tom profissional** (instituição financeira) e **guardrails** por categoria.
- **Confiança** do classificador + **destaques** (palavras-chave) que influenciaram a decisão.
- **Feedback do usuário** para corrigir classificação (grava em `data/feedback.jsonl`).

### Stack Técnica
- **Frontend**: HTML leve (Tailwind opcional) / fetch API.
- **Backend**: **FastAPI** + **Uvicorn**.
- **NLP**: `nltk` (stopwords PT), `scikit-learn` (baseline), `pdfminer.six` (PDF).
- **Opcional (IA externa)**: `transformers` (Hugging Face) / OpenAI.

### Arquitetura & Estrutura de Pastas
* **Email-Classification-Bot/**
    * 📄 .gitignore
    * 📄 README.md
    * 📁 **src/**
        * 📁 **components/**
            * 📄 Button.jsx
            * 📄 Card.jsx
        * 📁 **pages/**
            * 📄 HomePage.jsx
            * 📄 AboutPage.jsx
        * 📄 App.jsx
        * 📄 index.js
    * 📁 **public/**
        * 📄 index.html
        * 📄 favicon.ico

### Como Rodar Localmente (3 comandos)
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt && uvicorn app.main:app --reload
```
Abrir: <http://localhost:8000> (UI) • Docs: <http://localhost:8000/docs>

**Nota (NLTK)**: na primeira execução, o app pode baixar stopwords/rslp. Se preferir manualmente:
```python
import nltk; nltk.download('stopwords'); nltk.download('rslp')
```

### Variáveis de Ambiente (opcionais)
Crie um `.env` (ou use variáveis do sistema) se ativar IA externa:
```ini
USE_ZERO_SHOT=true              # habilita classificação zero-shot
HF_API_TOKEN=seu_token_aqui     # se usar Hugging Face Inference
OPENAI_API_KEY=seu_token_aqui   # se usar OpenAI para respostas
MODEL_ZERO_SHOT=joeddav/xlm-roberta-large-xnli
MODEL_REPLY=openai:gpt-4o-mini  # ou "hf:meta-llama/Meta-Llama-3.1-8B-Instruct"
```

---

## 🇺🇸 EN-US

### Overview
A simple web application that **classifies emails** as **Productive** or **Unproductive** and **suggests an appropriate automatic reply**. The goal is to **reduce manual triage** while keeping **clarity**, **speed**, and a **great user experience**.

### Key Features
- **Upload** `.txt`/`.pdf` files or **paste text** directly on the page.
- **Language preprocessing** (lowercase, PT-BR stopwords removal, stemming/lemmatization).
- **Classification** (Productive vs. Unproductive):
  - **Local baseline** (TF-IDF + Logistic Regression, no GPU/external), **or**
  - **Optional zero-shot** via Hugging Face / OpenAI (higher quality).
- **Suggested reply** with a **professional tone** (e.g., financial institution) and **guardrails** per category.
- **Classifier confidence** + **highlights** (keywords) that influenced the decision.
- **User feedback** to correct classification (saves to `data/feedback.jsonl`).

### Tech Stack
- **Frontend**: Lightweight HTML (optional Tailwind) / Fetch API.
- **Backend**: **FastAPI** + **Uvicorn**.
- **NLP**: `nltk` (PT stopwords), `scikit-learn` (baseline), `pdfminer.six` (PDF).
- **Optional (External AI)**: `transformers` (Hugging Face) / OpenAI.

### Architecture & Folder Structure
* **Email-Classification-Bot/**
    * 📄 .gitignore
    * 📄 README.md
    * 📁 **src/**
        * 📁 **components/**
            * 📄 Button.jsx
            * 📄 Card.jsx
        * 📁 **pages/**
            * 📄 HomePage.jsx
            * 📄 AboutPage.jsx
        * 📄 App.jsx
        * 📄 index.js
    * 📁 **public/**
        * 📄 index.html
        * 📄 favicon.ico

### How to Run Locally (3 commands)
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt && uvicorn app.main:app --reload
```
Open: <http://localhost:8000> (UI) • Docs: <http://localhost:8000/docs>

**Note (NLTK)**: on first run, the app may download stopwords/rslp. To do it manually:
```python
import nltk; nltk.download('stopwords'); nltk.download('rslp')
```

### Environment Variables (optional)
Create a `.env` file (or use system variables) if you enable external AI services:
```ini
USE_ZERO_SHOT=true              # enables zero-shot classification
HF_API_TOKEN=your_token_here    # if using Hugging Face Inference
OPENAI_API_KEY=your_token_here  # if using OpenAI for replies
MODEL_ZERO_SHOT=joeddav/xlm-roberta-large-xnli
MODEL_REPLY=openai:gpt-4o-mini  # or "hf:meta-llama/Meta-Llama-3.1-8B-Instruct"
```
