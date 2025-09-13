import secrets, hashlib, time
from typing import Tuple

def generate_otp() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"

def hash_otp(otp: str, salt: str | None = None) -> Tuple[str, str]:
    salt = salt or secrets.token_hex(8)
    h = hashlib.sha256((salt + otp).encode()).hexdigest()
    return h, salt

def verify_otp(otp: str, salt: str, otp_hash: str) -> bool:
    return hashlib.sha256((salt + otp).encode()).hexdigest() == otp_hash
