# backend/scripts/purge_supabase.py
import argparse
from dotenv import load_dotenv
load_dotenv()
from app.services.supabase_client import get_supabase

def chunked(lst, n=100):
    for i in range(0, len(lst), n):
        yield lst[i:i+n]

def main():
    p = argparse.ArgumentParser(description="Purge Supabase rows for a given email address")
    p.add_argument("--email", required=True, help="Seu endereço (ex.: bbitteste@gmail.com)")
    p.add_argument("--apply", action="store_true", help="Executar de fato. Sem --apply é dry-run")
    args = p.parse_args()

    sb = get_supabase()
    email = args.email.lower()

    ids = set()

    # 1) de quem enviou
    r1 = sb.table("emails").select("id").eq("from_email", email).execute()
    for row in (r1.data or []):
        ids.add(row["id"])

    # 2) quem recebeu (to_emails como json/array)
    try:
        r2 = sb.table("emails").select("id").contains("to_emails", [email]).execute()
        for row in (r2.data or []):
            ids.add(row["id"])
    except Exception:
        pass

    # 3) em cópia
    try:
        r3 = sb.table("emails").select("id").contains("cc_emails", [email]).execute()
        for row in (r3.data or []):
            ids.add(row["id"])
    except Exception:
        pass

    ids = list(ids)
    print(f"Encontrados {len(ids)} emails no Supabase relacionados a {email}")

    if not ids:
        return

    if not args.apply:
        print("Dry-run: nada foi removido. Use --apply para executar.")
        print("Exemplo de IDs:", ids[:10])
        return

    # Remover dependências primeiro
    for ch in chunked(ids, 200):
        sb.table("email_contents").delete().in_("email_id", ch).execute()
        sb.table("send_log").delete().in_("email_id", ch).execute()

    # Tokens de envio direcionados a esse e-mail
    sb.table("send_tokens").delete().eq("to_email", email).execute()

    # Por fim, a tabela principal
    for ch in chunked(ids, 200):
        sb.table("emails").delete().in_("id", ch).execute()

    print("Remoção concluída.")

if __name__ == "__main__":
    main()
