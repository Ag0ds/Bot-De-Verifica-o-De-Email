import os
from dotenv import load_dotenv
from imap_tools import MailBox

def main():
    load_dotenv()
    host = os.getenv("IMAP_HOST", "imap.gmail.com")
    user = os.getenv("IMAP_USER")
    pwd  = os.getenv("IMAP_PASS")
    folder = os.getenv("IMAP_FOLDER", "INBOX")

    print(f"Conectando a {host} como {user} (IMAPS 993 padrão)...")
    with MailBox(host).login(user, pwd, folder) as m:
        print("✅ Login OK.")
        print("📂 Pasta atual:", m.folder.get())
        print("🗂️  Algumas pastas:", [f.name for f in m.folder.list()[:5]])

if __name__ == "__main__":
    main()
