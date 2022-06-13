import json
from abc import ABC, abstractmethod
from typing import Union

from redis import Redis as RedisClient
from shortuuid import uuid

SupportedBackends = Union[RedisClient]


class TempPayloadStorage(ABC):
    """
    Provides a common interface to implement classes that allow temporarily storing payloads sent to NATS in the event
    that they exceed the max_payload property configured in the server.
    """

    def __init__(self, storage_client: SupportedBackends):
        self._client = storage_client

    @abstractmethod
    def is_stored(self, payload: bytes) -> bool:  # pragma: no cover
        """
        Indicates whether a payload is stored to a particular backend.

        :param payload: the payload as a sequence of bytes
        :returns: a boolean
        """
        pass

    @abstractmethod
    def store(self, payload: bytes) -> bytes:  # pragma: no cover
        """
        Stores a payload to the storage backend.

        :param payload: the payload as a sequence of bytes
        :returns: a sequence of bytes representing a token, which serves as a way to recover a stored payload at the
                  SUB end of a NATS PUB/SUB flow
        """
        pass

    @abstractmethod
    def recover(self, token: bytes) -> bytes:  # pragma: no cover
        """
        Recovers a payload from the storage backend using a particular token.

        :param token: the token used to recover the payload
        :returns: the payload as a sequence of bytes
        """
        pass


class Redis(TempPayloadStorage):
    """
    Implements a temporary payload storage based on Redis.
    """

    TMP_PAYLOAD_PREFIX = b"_NATS_TMP"

    def is_stored(self, payload: bytes) -> bool:
        """
        Indicates whether a payload is stored to a Redis backend by checking if it starts with a particular prefix.

        :param payload: the payload as a sequence of bytes
        :returns: a boolean
        """
        return payload.startswith(self.TMP_PAYLOAD_PREFIX)

    def store(self, payload: bytes) -> bytes:
        """
        Stores a payload to a Redis backend.

        :param payload: the payload as a sequence of bytes
        :returns: a sequence of bytes representing a token, which serves as a way to recover a stored payload at the
                  SUB end of a NATS PUB/SUB flow
        """
        key = f"{self.TMP_PAYLOAD_PREFIX.decode()} {uuid()}".encode()
        self._client.set(name=key, value=payload, ex=300)

        return key

    def recover(self, token: bytes) -> bytes:
        """
        Recovers a payload from a Redis backend using a particular token.

        :param token: the token used to recover the payload
        :returns: the payload as a sequence of bytes
        """
        return self._client.get(name=token)


class RedisLegacy(TempPayloadStorage):
    """
    Implements a temporary payload storage based on Redis and old-style tokens. Suitable only for backwards
    compatibility with the old EventBus abstraction.
    """

    def is_stored(self, payload: bytes) -> bool:
        """
        Indicates whether a payload is stored to a Redis backend using old-style tokens.

        :param payload: the payload as a sequence of bytes
        :returns: a boolean
        """
        asjson = json.loads(payload)
        return asjson.get("token") is not None and asjson.get("is_stored") is True

    def store(self, payload: bytes) -> bytes:
        """
        Stores a payload to a Redis backend using an old-style token.

        :param payload: the payload as a sequence of bytes
        :returns: a sequence of bytes representing a dict with shape {"is_stored": <bool>, "token": <str>}, which
                  serves as a way to recover a stored payload at the SUB end of a NATS PUB/SUB flow
        """
        token = uuid()
        self._client.set(name=token, value=payload, ex=300)

        return json.dumps({"is_stored": True, "token": token}).encode()

    def recover(self, token: bytes) -> bytes:
        """
        Recovers a payload from a Redis backend using a particular old-style token.

        :param token: the token used to recover the payload
        :returns: the payload as a sequence of bytes
        """
        return self._client.get(name=json.loads(token)["token"])
