import json, time
from pathlib import Path

LOG_FILE = Path("audit_log.jsonl")

def log_event(event_type, user, payload):
    entry = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "type": event_type,
        "user": user,
        "data": payload
    }
    LOG_FILE.write_text(LOG_FILE.read_text() + json.dumps(entry) + "\n" if LOG_FILE.exists() else json.dumps(entry) + "\n")
    return entry
