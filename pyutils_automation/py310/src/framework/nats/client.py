import asyncio
import logging
import ssl
from functools import wraps
from typing import Any, Awaitable, Callable, Dict, List, Optional

from framework.nats.exceptions import BadSubjectError, NatsConnectionError, ResponseTimeoutError
from framework.nats.temp_payload_storage import TempPayloadStorage
from nats import errors
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
)
from nats.aio.client import Client as Client_
from nats.aio.client import Credentials, ErrorCallback, JWTCallback, SignatureCallback, Subscription
from nats.aio.msg import Msg

logger = logging.getLogger(__name__)


class Client(Client_):
    def __init__(self, temp_payload_storage: TempPayloadStorage):
        self._temp_payload_storage = temp_payload_storage
        super().__init__()

    def _exceeds_max_payload_size(self, payload: bytes) -> bool:
        """
        Indicates whether a payload is larger than the maximum allowed size by the NATS server.

        :param payload: the payload as a sequence of bytes
        :returns: a boolean
        """
        return len(payload) > self.max_payload

    def _pre_recover_cb(self, cb: Callable[[Msg], Awaitable[None]]) -> Callable[[Msg], Awaitable[None]]:
        """
        Decorates a callback bound to a NATS subject to recover a payload stored to a particular backend before the
        callback is invoked.

        :param cb: the callback bound to a NATS subject
        :returns: a callback with the same signature as the original callback, which takes the payload recovered from
                  the storage backend
        """

        @wraps(cb)
        async def inner(msg: Msg):
            if self._temp_payload_storage.is_stored(msg.data):
                logger.warning(
                    f"Message received in subject {msg.subject} exceeds the maximum size allowed by NATS. Recovering "
                    "it from the external storage..."
                )
                msg.data = self._temp_payload_storage.recover(msg.data)

            await cb(msg)

        return inner

    async def connect(
        self,
        servers: List[str] = None,
        error_cb: Optional[ErrorCallback] = None,
        disconnected_cb: Optional[Callback] = None,
        closed_cb: Optional[Callback] = None,
        discovered_server_cb: Optional[Callback] = None,
        reconnected_cb: Optional[Callback] = None,
        name: Optional[str] = None,
        pedantic: bool = False,
        verbose: bool = False,
        allow_reconnect: bool = True,
        connect_timeout: int = DEFAULT_CONNECT_TIMEOUT,
        reconnect_time_wait: int = DEFAULT_RECONNECT_TIME_WAIT,
        max_reconnect_attempts: int = DEFAULT_MAX_RECONNECT_ATTEMPTS,
        ping_interval: int = DEFAULT_PING_INTERVAL,
        max_outstanding_pings: int = DEFAULT_MAX_OUTSTANDING_PINGS,
        dont_randomize: bool = False,
        flusher_queue_size: int = DEFAULT_MAX_FLUSHER_QUEUE_SIZE,
        no_echo: bool = False,
        tls: Optional[ssl.SSLContext] = None,
        tls_hostname: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        token: Optional[str] = None,
        drain_timeout: int = DEFAULT_DRAIN_TIMEOUT,
        signature_cb: Optional[SignatureCallback] = None,
        user_jwt_cb: Optional[JWTCallback] = None,
        user_credentials: Optional[Credentials] = None,
        nkeys_seed: Optional[str] = None,
    ) -> None:
        """
        Establishes a connection to the NATS server.

        :raises NatsConnectionError: if the connection with NATS fails
        """
        try:
            logger.info(f"Connecting to NATS servers: {servers}...")
            await super().connect(
                servers=servers,
                error_cb=error_cb,
                disconnected_cb=disconnected_cb,
                closed_cb=closed_cb,
                discovered_server_cb=discovered_server_cb,
                reconnected_cb=reconnected_cb,
                name=name,
                pedantic=pedantic,
                verbose=verbose,
                allow_reconnect=allow_reconnect,
                connect_timeout=connect_timeout,
                reconnect_time_wait=reconnect_time_wait,
                max_reconnect_attempts=max_reconnect_attempts,
                ping_interval=ping_interval,
                max_outstanding_pings=max_outstanding_pings,
                dont_randomize=dont_randomize,
                flusher_queue_size=flusher_queue_size,
                no_echo=no_echo,
                tls=tls,
                tls_hostname=tls_hostname,
                user=user,
                password=password,
                token=token,
                drain_timeout=drain_timeout,
                signature_cb=signature_cb,
                user_jwt_cb=user_jwt_cb,
                user_credentials=user_credentials,
                nkeys_seed=nkeys_seed,
            )
            logger.info(f"Connected to NATS servers successfully")
        except (errors.NoServersError, OSError, errors.Error, asyncio.TimeoutError) as e:
            raise NatsConnectionError from e

    async def subscribe(
        self,
        subject: str,
        queue: str = "",
        cb: Optional[Callable[[Msg], Awaitable[None]]] = None,
        future: Optional[asyncio.Future] = None,
        max_msgs: int = 0,
        pending_msgs_limit: int = DEFAULT_SUB_PENDING_MSGS_LIMIT,
        pending_bytes_limit: int = DEFAULT_SUB_PENDING_BYTES_LIMIT,
    ) -> Subscription:
        """
        Binds a NATS subject to a particular callback.

        Note that the callback is decorated with a helper to recover messages stored to a backend before it's invoked.

        :raises NatsConnectionError: if the connection with NATS fails
        :raises BadSubjectError: if the subject is an empty string
        """
        try:
            logger.info(f"Subscribing to subject {subject} with queue group {queue}...")
            cb = self._pre_recover_cb(cb)
            sub = await super().subscribe(
                subject=subject,
                queue=queue,
                cb=cb,
                future=future,
                max_msgs=max_msgs,
                pending_msgs_limit=pending_msgs_limit,
                pending_bytes_limit=pending_bytes_limit,
            )
            logger.info(f"Subscribed to subject successfully")
            return sub
        except (errors.ConnectionClosedError, errors.ConnectionDrainingError) as e:
            raise NatsConnectionError from e
        except errors.BadSubjectError as e:
            raise BadSubjectError(subject) from e

    async def publish(
        self, subject: str, payload: bytes = b"", reply: str = "", headers: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Publishes a payload to a particular subject.

        If the payload is too large for NATS to handle, it is stored to a storage backend before publishing it.

        :raises NatsConnectionError: if the connection with NATS fails
        :raises BadSubjectError: if the subject is an empty string
        """
        if self._exceeds_max_payload_size(payload):
            logger.warning(
                "Payload exceeds the maximum size allowed by NATS. Storing it to the external storage before "
                f"publishing to subject {subject}..."
            )
            payload = self._temp_payload_storage.store(payload)

        try:
            logger.info(f"Publishing payload to subject {subject}...")
            await super().publish(
                subject=subject,
                payload=payload,
                reply=reply,
                headers=headers,
            )
            logger.info(f"Payload published to subject {subject} successfully")
        except (errors.ConnectionClosedError, errors.ConnectionDrainingError) as e:
            raise NatsConnectionError from e
        except errors.BadSubjectError as e:
            raise BadSubjectError(subject) from e

    async def request(
        self,
        subject: str,
        payload: bytes = b"",
        timeout: float = 0.5,
        old_style: bool = False,
        headers: Dict[str, Any] = None,
    ) -> Msg:
        """
        Publishes a payload to a particular subject and awaits for a response from another subscriber with interest
        in that subject, which must respond to the request before reaching a timeout.

        If the request payload is too large for NATS to handle, it is stored to a storage backend before publishing it.

        If the response payload is identified as stored to a backend, it is recovered from there and returned.

        :returns: a NATS message holding a response to the original request
        :raises NatsConnectionError: if the connection with NATS fails
        :raises BadSubjectError: if the subject is an empty string
        :raises TimeoutError: if a subscriber doesn't respond to the request in time
        """
        try:
            logger.info(f"Requesting a response from subject {subject}...")
            response = await super().request(
                subject=subject,
                payload=payload,
                timeout=timeout,
                old_style=old_style,
                headers=headers,
            )
            logger.info(f"Response received from a replier subscribed to subject {subject}")
        except (errors.ConnectionClosedError, errors.ConnectionDrainingError) as e:
            raise NatsConnectionError from e
        except errors.BadSubjectError as e:
            raise BadSubjectError(subject) from e
        except errors.TimeoutError as e:
            raise ResponseTimeoutError(subject) from e

        if self._temp_payload_storage.is_stored(response.data):
            logger.warning(
                f"Response received from subject {subject} exceeds the maximum size allowed by NATS. Recovering it "
                "from the external storage..."
            )
            response.data = self._temp_payload_storage.recover(response.data)

        return response
