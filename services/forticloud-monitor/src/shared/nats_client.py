import logging
from dataclasses import dataclass, field
from typing import List, Protocol, TypeVar

from framework.nats.client import Client
from framework.nats.models import Subscription
from pydantic import BaseModel

R = TypeVar("R")


log = logging.getLogger(__name__)


class NatsSettings(BaseModel):
    servers: List[str]


class NatsConsumer(Protocol):
    def subscription(self) -> Subscription:
        pass


@dataclass
class NatsClient:
    """
    A framework nats client wrapper to deal with payload and response parsing.
    """

    settings: NatsSettings
    framework_client: Client
    is_connected: bool = field(init=False, default=False)

    async def add(self, consumer: NatsConsumer):
        log.debug(f"add(consumer={consumer})")
        if not self.is_connected:
            await self.connect()
            self.is_connected = True

        await self.framework_client.subscribe(**consumer.subscription().__dict__)

    async def connect(self):
        log.debug("_connect()")
        await self.framework_client.connect(servers=self.settings.servers)
