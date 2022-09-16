import logging
from dataclasses import asdict, dataclass, field
from typing import Any, Generic, List, Protocol, Type, TypeVar

from framework.nats.client import Client
from framework.nats.models import Subscription
from pydantic import BaseModel, BaseSettings, Field
from pydantic.generics import GenericModel
from shortuuid import uuid

# Response body generic type
R = TypeVar("R")


log = logging.getLogger(__name__)


class NatsSettings(BaseSettings):
    servers: List[str] = Field(..., env="NATS_SERVERS")


class NatsResponse(GenericModel, Generic[R]):
    """
    Model of a nats response
    """

    status: int
    body: R


class NatsRequest(BaseModel):
    """
    Model of a nats request
    """

    request_id: str = Field(default_factory=uuid)
    body: Any

    def serialize(self) -> bytes:
        return self.json(separators=(",", ":")).encode()


class NatsConsumer(Protocol):
    def subscription(self) -> Subscription:
        pass


@dataclass
class NatsClient:
    """
    A framework nats client wrapper to deal with payload and response parsing.
    """

    framework_client: Client
    settings: NatsSettings = NatsSettings()
    is_connected: bool = field(init=False, default=False)

    async def request(
        self,
        subject: str,
        payload: Any,
        response_body_type: Type[R] = Any,
    ) -> NatsResponse[R]:
        """
        A request wrapper that deals with serializing and deserializing requests and responses.
        The response body will be the same type as the one passed to the `response_body_type` type parameter.

        :param subject: the nats subject in which issue the request
        :param payload: the payload data to be sent in the request
        :param response_body_type: the expected type of the response body
        :return:
        """
        log.debug(f"request(subject={subject}, payload={payload}, response_body_type={response_body_type})")
        nats_payload = NatsRequest(body=payload).serialize()

        response = await self.framework_client.request(subject, nats_payload)
        log.debug(f"request():framework_client.request()={response}")

        nats_response = NatsResponse.parse_raw(response.data)
        if response_body_type == Any:
            pass
        elif issubclass(response_body_type, BaseModel):
            nats_response.body = response_body_type.parse_obj(nats_response.body)
        else:
            nats_response.body = response_body_type(nats_response.body)

        return nats_response

    async def add(self, consumer: NatsConsumer):
        log.debug(f"add(consumer={consumer})")
        if not self.is_connected:
            await self.connect()
            self.is_connected = True

        await self.framework_client.subscribe(**asdict(consumer.subscription()))

    async def connect(self):
        log.debug("_connect()")
        await self.framework_client.connect(servers=self.settings.servers)
