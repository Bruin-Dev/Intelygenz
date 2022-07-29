import asyncio
import ssl
from typing import Any, Awaitable, Callable, Optional

from dataclasses import dataclass, field
from nats.aio.client import (
    DEFAULT_CONNECT_TIMEOUT,
    DEFAULT_DRAIN_TIMEOUT,
    DEFAULT_MAX_FLUSHER_QUEUE_SIZE,
    DEFAULT_MAX_OUTSTANDING_PINGS,
    DEFAULT_MAX_RECONNECT_ATTEMPTS,
    DEFAULT_PING_INTERVAL,
    DEFAULT_RECONNECT_TIME_WAIT,
    DEFAULT_SUB_PENDING_BYTES_LIMIT,
    DEFAULT_SUB_PENDING_MSGS_LIMIT,
    Callback,
    Credentials,
    ErrorCallback,
    JWTCallback,
    SignatureCallback,
)
from nats.aio.msg import Msg

DEFAULT_SERVERS = ["nats://127.0.0.1:4222"]


@dataclass(kw_only=True)
class Connection:
    servers: list[str] = field(default_factory=lambda: DEFAULT_SERVERS.copy())
    error_cb: Optional[ErrorCallback] = None
    disconnected_cb: Optional[Callback] = None
    closed_cb: Optional[Callback] = None
    discovered_server_cb: Optional[Callback] = None
    reconnected_cb: Optional[Callback] = None
    name: Optional[str] = None
    pedantic: bool = False
    verbose: bool = False
    allow_reconnect: bool = True
    connect_timeout: int = DEFAULT_CONNECT_TIMEOUT
    reconnect_time_wait: int = DEFAULT_RECONNECT_TIME_WAIT
    max_reconnect_attempts: int = DEFAULT_MAX_RECONNECT_ATTEMPTS
    ping_interval: int = DEFAULT_PING_INTERVAL
    max_outstanding_pings: int = DEFAULT_MAX_OUTSTANDING_PINGS
    dont_randomize: bool = False
    flusher_queue_size: int = DEFAULT_MAX_FLUSHER_QUEUE_SIZE
    no_echo: bool = False
    tls: Optional[ssl.SSLContext] = None
    tls_hostname: Optional[str] = None
    user: Optional[str] = None
    password: Optional[str] = None
    token: Optional[str] = None
    drain_timeout: int = DEFAULT_DRAIN_TIMEOUT
    signature_cb: Optional[SignatureCallback] = None
    user_jwt_cb: Optional[JWTCallback] = None
    user_credentials: Optional[Credentials] = None
    nkeys_seed: Optional[str] = None


@dataclass(kw_only=True)
class Subscription:
    subject: str
    queue: str = ""
    cb: Optional[Callable[[Msg], Awaitable[None]]] = None
    future: Optional[asyncio.Future] = None
    max_msgs: int = 0
    pending_msgs_limit: int = DEFAULT_SUB_PENDING_MSGS_LIMIT
    pending_bytes_limit: int = DEFAULT_SUB_PENDING_BYTES_LIMIT


@dataclass(kw_only=True)
class Publish:
    subject: str
    payload: bytes = b""
    reply: str = ""
    headers: Optional[dict[str, Any]] = None


@dataclass(kw_only=True)
class Request:
    subject: str
    payload: bytes = b""
    timeout: float = 1.0
    old_style: bool = False
    headers: dict[str, Any] = None
