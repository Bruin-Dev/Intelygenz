import json
from typing import Any, Dict


def to_json_bytes(message: Dict[str, Any]):
    return json.dumps(message, default=str, separators=(",", ":")).encode()
