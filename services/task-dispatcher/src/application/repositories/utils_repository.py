import json


def to_json_bytes(message: dict):
    return json.dumps(message, default=str, separators=(",", ":")).encode()
