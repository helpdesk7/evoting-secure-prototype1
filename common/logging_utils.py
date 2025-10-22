"""
common/logging_utils.py
Implements anonymized session logging utilities for SR-08.
All logs avoid storing any personally identifiable information (PII).
"""

import hashlib
import json
from datetime import datetime
from pathlib import Path

LOG_FILE = Path(__file__).resolve().parent.parent / "anon_sessions.log"


def anonymize_value(value: str) -> str:
    """Return a short SHA256 digest for anonymization."""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]


def log_session(
    event: str, user_identifier: str, ip: str = "unknown", extra: dict | None = None
):
    """
    Append an anonymized session event to the log file.
    Args:
        event: e.g. "login", "logout", "request"
        user_identifier: something unique per user (email/ID) — will be hashed
        ip: optional client IP
        extra: optional additional metadata
    """
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event": event,
        "user_hash": anonymize_value(user_identifier),
        "ip_hash": anonymize_value(ip),
        "extra": extra or {},
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


if __name__ == "__main__":
    # simple manual test
    log_session("test", "user@example.com", "127.0.0.1", {"note": "manual test"})
    print(f"✅ Logged test entry to {LOG_FILE}")
