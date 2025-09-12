from dotenv import load_dotenv
from app.services.email_ingest import fetch_unread
from app.pipeline import translate_email

def main():
    load_dotenv()

    print("Lendo últimos e-mails não lidos do IMAP...\n")
    for i, raw in enumerate(fetch_unread(limit=3), start=1):
        res = translate_email(
            subject=raw["subject"],
            body_text=raw["text"],
            body_html=raw["html"],
            attachments=raw["attachments"],
        )
        print(f"=== EMAIL {i} ===")
        print("Assunto:", res["subject"])
        print("Tem texto de PDF?:", res["has_pdf_text"])
        print("Tamanho (chars):", res["length"])
        print("\n--- TEXTO LIMPO ---\n")
        # Mostra apenas os primeiros 1200 chars para não poluir
        txt = res["text"][:1200]
        print(txt)
        if len(res["text"]) > 1200:
            print("\n...[truncado]...\n")

if __name__ == "__main__":
    main()
