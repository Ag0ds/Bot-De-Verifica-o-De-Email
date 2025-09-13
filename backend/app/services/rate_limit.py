import os, time
from typing import Tuple

_BUCKETS = {}

def _now() -> float:
    return time.time()

def _get_limits():
    hourly_email = int(os.getenv("RATE_LIMIT_EMAIL_HOURLY", "3"))
    daily_email = int(os.getenv("RATE_LIMIT_EMAIL_DAILY", "10"))
    hourly_ip = int(os.getenv("RATE_LIMIT_IP_HOURLY", "10"))
    return hourly_email, daily_email, hourly_ip

def _incr(key: str, ttl: int):
    now = _now()
    bucket = _BUCKETS.get(key, [])
    bucket = [t for t in bucket if now - t < ttl]
    bucket.append(now)
    _BUCKETS[key] = bucket
    return len(bucket)

def check_email_quota(to_email: str) -> Tuple[bool, str]:
    hourly, daily, _ = _get_limits()
    h = _incr(f"email:h:{to_email}", 3600)
    d = _incr(f"email:d:{to_email}", 86400)
    if h > hourly:
        return False, f"limite horário excedido ({hourly}/h)"
    if d > daily:
        return False, f"limite diário excedido ({daily}/dia)"
    return True, ""

def check_ip_rate(ip: str) -> Tuple[bool, str]:
    _, _, hourly_ip = _get_limits()
    h = _incr(f"ip:h:{ip}", 3600)
    if h > hourly_ip:
        return False, f"limite por IP excedido ({hourly_ip}/h)"
    return True, ""
