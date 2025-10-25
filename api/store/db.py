from typing import Dict, List, Any
from hashlib import sha256
import json

# toy in-memory "db"
VOTERS: Dict[str, dict] = {
    "alice": {"address": {"line1": "1 Main St", "city": "Metro", "zip": "10000"}}
}
AUDIT: List[dict] = []

def etag_of(obj: Any) -> str:
    return sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()
