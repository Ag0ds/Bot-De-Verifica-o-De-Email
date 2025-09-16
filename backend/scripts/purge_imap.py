# backend/scripts/purge_imap.py
import os, argparse
from datetime import date
from imap_tools import MailBox, A
from dotenv import load_dotenv

load_dotenv()  # <-- lê o .env da pasta

def main():
    p = argparse.ArgumentParser(description="Purge IMAP mailbox")
    p.add_argument("--since", help="YYYY-MM-DD (apaga do período em diante). Se omitir, apaga TUDO.", default=None)
    p.add_argument("--hard", action="store_true", help="Apagar PERMANENTEMENTE (delete + expunge).")
    p.add_argument("--folder", default=None, help="Pasta (default: IMAP_FOLDER ou INBOX)")
    p.add_argument("--dry", action="store_true", help="Somente listar, não apagar")
    # sobrescritas opcionais
    p.add_argument("--host")
    p.add_argument("--user")
    p.add_argument("--password")
    args = p.parse_args()

    host   = args.host or os.getenv("IMAP_HOST", "imap.gmail.com")
    user   = args.user or os.getenv("IMAP_USER")
    passwd = args.password or os.getenv("IMAP_PASS")
    folder = args.folder or os.getenv("IMAP_FOLDER", "INBOX")

    if not (host and user and passwd):
        raise SystemExit("IMAP_HOST/IMAP_USER/IMAP_PASS faltando (env ou parâmetros).")

    with MailBox(host).login(user, passwd, folder) as mbox:
        crit = A(all=True)
        if args.since:
            y, m, d = map(int, args.since.split("-"))
            crit = A(date_gte=date(y, m, d))

        uids = [msg.uid for msg in mbox.fetch(crit, mark_seen=False)]
        print(f"[{folder}] encontrados {len(uids)} e-mails para remover (since={args.since or 'ALL'})")

        if not uids or args.dry:
            if args.dry and uids:
                print("Exemplo de UIDs:", uids[:10])
            return

        if args.hard:
            mbox.delete(uids); mbox.expunge()
            print("Removidos permanentemente (delete + expunge).")
        else:
            trash = os.getenv("IMAP_TRASH_FOLDER", "[Gmail]/Trash")  # ajuste para seu provedor
            try:
                mbox.move(uids, trash)
                print(f"Movidos para {trash}.")
            except Exception as e:
                print(f"Falhou mover para Trash ({e}), tentando delete+expunge...")
                mbox.delete(uids); mbox.expunge()
                print("Removidos permanentemente (fallback).")

if __name__ == "__main__":
    main()
