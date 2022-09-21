import asyncio
import logging
import signal
from asyncio import AbstractEventLoop

from aiohttp import ClientSession
from framework.logging.formatters import Papertrail as PapertrailFormatter
from framework.logging.formatters import Standard as StandardFormatter
from framework.logging.handlers import Papertrail as PapertrailHandler
from framework.logging.handlers import Stdout as StdoutHandler
from framework.nats.client import Client as FrameworkClient
from framework.nats.temp_payload_storage import RedisLegacy as PayloadStorage
from redis.client import Redis

from clients import NatsClient
from clients.http_client import HttpClient
from settings import Settings
from usecases.check_device import CheckDevice, CreateTicket, DeviceConsumer, GetDevice

log = logging.getLogger()
log.setLevel(logging.DEBUG)


class Application:
    redis_client: Redis
    nats_client: NatsClient
    http_client: HttpClient

    async def start(self, settings: Settings):
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

        log.info("Starting forticloud-monitor ...")
        log.info("==========================================================")

        # Redis client
        log.info(f"Connecting to Redis(host={settings.redis_host}, port={settings.redis_port}) ...")
        self.redis_client = Redis(host=settings.redis_host, port=settings.redis_port, decode_responses=True)
        self.redis_client.ping()
        log.info(f"Connected to Redis")
        log.info("----------------------------------------------------------")

        # Nats client
        log.info(f"Initializing NatsClient ...")
        framework_client = FrameworkClient(temp_payload_storage=PayloadStorage(self.redis_client))
        self.nats_client = NatsClient(settings.nats, framework_client)
        await self.nats_client.connect()
        log.info(f"NatsClient initialized")
        log.info("----------------------------------------------------------")

        # Http clients
        self.http_client = HttpClient(ClientSession(settings.bruin_base_url))

        # Check device usecase
        log.info(f"Adding CheckDevice consumer ...")
        check_device = CheckDevice(GetDevice(self.http_client), CreateTicket(self.http_client))
        device_consumer = DeviceConsumer(settings.device_consumer, check_device)
        await self.nats_client.add(device_consumer)
        log.info("CheckDevice consumer added")

        log.info("==========================================================")
        log.info("Forticloud monitor started")

    async def close(self, stop_loop: bool = True):
        log.info("Closing Forticloud monitor ...")
        log.info("==========================================================")

        await self.http_client.close()
        log.info("Http client closed")
        await self.nats_client.close()
        log.info("Nats client closed")
        self.redis_client.close()
        log.info("Redis client closed")

        if stop_loop:
            asyncio.get_running_loop().stop()
            log.info("Event loop stopped")

        log.info("==========================================================")
        log.info("Forticloud monitor closed")


async def start(application: Application, settings: Settings, loop: AbstractEventLoop):
    loop.create_task(application.start(settings))
    loop.add_signal_handler(signal.SIGINT, lambda: loop.create_task(application.close()))
    loop.add_signal_handler(signal.SIGQUIT, lambda: loop.create_task(application.close()))


if __name__ == "__main__":
    main_loop = asyncio.new_event_loop()
    asyncio.run(start(Application(), Settings(), main_loop))
    main_loop.run_forever()
