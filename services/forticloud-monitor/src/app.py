import asyncio

from framework.nats.client import Client
from framework.nats.temp_payload_storage import RedisLegacy as PayloadStorage
from redis.client import Redis

from clients import NatsClient
from settings import RedisSettings
from usecases.check_device import CheckDevice, CheckDeviceConsumer, DeviceRepository, TicketRepository

# Redis
settings = RedisSettings()
redis_client = Redis(host=settings.redis_host, port=settings.redis_port, decode_responses=True)
redis_client.ping()

# Nats client
framework_client = Client(temp_payload_storage=PayloadStorage(redis_client))
nats_client = NatsClient(framework_client)

# Check device usecase
device_repository = DeviceRepository()
ticket_repository = TicketRepository(nats_client)
check_device = CheckDevice(device_repository, ticket_repository)
check_device_consumer = CheckDeviceConsumer(check_device)


async def start():
    await nats_client.add(check_device_consumer)


if __name__ == "__main__":
    asyncio.run(start())
