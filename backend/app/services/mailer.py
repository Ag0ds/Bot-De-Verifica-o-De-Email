import os, smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

def send_email(to_email: str, subject: str, body: str) -> str:
    host = os.getenv("SMTP_HOST"); port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER"); pwd = os.getenv("SMTP_PASS")
    sender = os.getenv("SENDER_EMAIL"); sender_name = os.getenv("SENDER_NAME", "AutoU Bot")

    if not all([host, port, user, pwd, sender]):
        raise RuntimeError("SMTP vars ausentes no .env")

    msg = MIMEText(body, _charset="utf-8")
    msg["Subject"] = subject
    msg["From"] = formataddr((sender_name, sender))
    msg["To"] = to_email

    with smtplib.SMTP(host, port) as server:
        server.starttls()
        server.login(user, pwd)
        server.sendmail(sender, [to_email], msg.as_string())

    return "OK"
