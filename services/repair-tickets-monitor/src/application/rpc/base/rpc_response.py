from typing import Any, Dict

from dataclasses import dataclass

OK_STATUS = 200
UNKNOWN_STATUS = -1


@dataclass
class RpcResponse:
    status: int
    body: Dict[str, Any]

    @classmethod
    def from_response(cls, response: Any):
        if not isinstance(response, dict):
            return cls(status=UNKNOWN_STATUS, body={})

        try:
            status = int(str(response.get("status")))
        except ValueError:
            status = UNKNOWN_STATUS

        body = response.get("body", {})
        if not isinstance(body, dict):
            body = {}

        return cls(status=status, body=body)

    def is_ok(self):
        return self.status == OK_STATUS
