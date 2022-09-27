import base64
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, Optional


@dataclass
class BruinCredentials:
    client_id: str
    client_secret: str

    def b64encoded(self) -> str:
        return base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()


@dataclass
class BruinToken:
    value: str = ""
    expires_in: int = -1
    issued_at: datetime = field(default_factory=lambda: datetime.utcnow())

    def is_expired(self) -> bool:
        return self.issued_at + timedelta(seconds=self.expires_in) <= datetime.utcnow()


@dataclass(kw_only=True)
class BruinRequest:
    path: str
    method: str
    query_params: Dict[str, str] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)
    json: Optional[str] = None


@dataclass
class BruinResponse:
    status: int
    text: str


class RefreshTokenError(Exception):
    pass
