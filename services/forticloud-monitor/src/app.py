import asyncio
import logging

from framework.logging.formatters import Papertrail as PapertrailFormatter
from framework.logging.formatters import Standard as StandardFormatter
from framework.logging.handlers import Papertrail as PapertrailHandler
from framework.logging.handlers import Stdout as StdoutHandler
from framework.nats.client import Client as FrameworkClient
from framework.nats.temp_payload_storage import RedisLegacy as PayloadStorage
from redis.client import Redis

from settings import Settings
from shared import NatsClient
from usecases.check_device import BuildTicket, CheckDevice, DeviceConsumer, GetDevice, StoreTicket

log = logging.getLogger(__name__)


async def start(settings: Settings):
    # Logging configuration
    stdout_handler = StdoutHandler()
    stdout_handler.setFormatter(StandardFormatter(environment_name=settings.environment_name))
    log.addHandler(stdout_handler)

    if settings.is_papertrail_active:
        papertrail_handler = PapertrailHandler(host=settings.papertrail_host, port=settings.papertrail_port)
        papertrail_handler.setFormatter(
            PapertrailFormatter(
                environment_name=settings.environment_name,
                papertrail_prefix=settings.papertrail_prefix,
            )
        )
        log.addHandler(papertrail_handler)

    log.info("Starting forticloud-monitor")

    # Redis client
    redis_client = Redis(host=settings.redis_host, port=settings.redis_port, decode_responses=True)
    redis_client.ping()
    log.info(f"Connected to Redis(host={settings.redis_host}, port={settings.redis_port})...")

    # Nats client
    framework_client = FrameworkClient(temp_payload_storage=PayloadStorage(redis_client))
    nats_client = NatsClient(settings.nats, framework_client)
    log.info(f"NatsClient initialized")

    # Check device usecase
    check_device = CheckDevice(GetDevice(), StoreTicket(settings.store_ticket, nats_client), BuildTicket())
    log.info(f"CheckDevice usecase initialized")

    device_consumer = DeviceConsumer(settings.device_consumer, check_device)
    await nats_client.add(device_consumer)
    log.info("CheckDevice consumer added")


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.create_task(start(Settings()))
    loop.run_forever()
