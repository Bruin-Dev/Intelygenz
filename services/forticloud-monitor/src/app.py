import asyncio
import logging
import signal
from asyncio import AbstractEventLoop
from dataclasses import dataclass
from typing import Optional

from bruin_client import BruinClient
from forticloud_client.client import ForticloudClient
from framework.http.server import Config as HealthConfig
from framework.nats.client import Client as FrameworkClient
from framework.nats.temp_payload_storage import RedisLegacy as TempPayloadStorage
from redis.client import Redis

from application.actions import CheckDevice
from application.clients import NatsClient
from application.consumers import ApConsumer, SwitchConsumer
from application.repositories import BruinRepository, ForticloudRepository
from config.config import Config
from health_server import HealthServer

log = logging.getLogger()
log.setLevel(logging.DEBUG)


@dataclass
class Application:
    health_server: Optional[HealthServer] = None
    bruin_client: Optional[BruinClient] = None
    forticloud_client: Optional[ForticloudClient] = None
    redis: Optional[Redis] = None
    nats_client: Optional[NatsClient] = None

    async def start(self, config: Config):
        # Logging configuration
        log.addHandler(config.stout_handler)
        if config.is_papertrail_active:
            log.addHandler(config.papetrail_handler)

        log.info("Starting forticloud-monitor ...")
        log.info("==========================================================")

        # Health server
        self.health_server = HealthServer(HealthConfig(config.health_server_port))
        await self.health_server.run()
        log.info("==> Health server started")

        # Bruin client
        self.bruin_client = BruinClient(config.bruin_base_url, config.bruin_login_url, config.bruin_credentials)
        log.info("==> Bruin client connected")

        # Forticloud client
        self.forticloud_client = ForticloudClient(config.forticloud_config)
        log.info("==> Forticloud client connected")

        # NATS Redis
        self.redis = Redis(host=config.redis_host, port=config.redis_port, decode_responses=True)
        self.redis.ping()
        log.info("==> NATS Redis support connected")

        # NATS
        storage_client = Redis(host=config.redis_host)
        temp_payload_storage = TempPayloadStorage(storage_client)
        framework_client = FrameworkClient(temp_payload_storage)
        self.nats_client = NatsClient(config.nats_settings, framework_client)
        await self.nats_client.connect()
        log.info("==> NATS connected")

        # Repositories
        bruin_repository = BruinRepository(self.bruin_client)
        forticloud_repository = ForticloudRepository(self.forticloud_client)
        # Actions
        check_device = CheckDevice(forticloud_repository, bruin_repository)
        # Consumers
        await self.nats_client.add(ApConsumer(config.ap_consumer_settings, check_device))
        await self.nats_client.add(SwitchConsumer(config.switch_consumer_settings, check_device))
        log.info("==> Application initialized")

        log.info("==========================================================")
        log.info("Forticloud monitor started")

    async def close(self, stop_loop: bool = True):
        log.info("Closing Forticloud monitor ...")
        log.info("==========================================================")

        if self.health_server:
            await self.health_server.close()
            log.info("==> Health server closed")
        if self.bruin_client:
            await self.bruin_client.close()
            log.info("==> Bruin client closed")
        if self.redis:
            self.redis.close()
            log.info("==> Redis closed")
        if self.nats_client:
            await self.nats_client.close()
            log.info("==> NATS closed")
        if stop_loop:
            asyncio.get_running_loop().stop()
            log.info("==> Event loop stopped")

        log.info("==========================================================")
        log.info("Forticloud monitor closed")


def start(application: Application, config: Config, loop: AbstractEventLoop):
    loop.create_task(application.start(config))
    loop.add_signal_handler(signal.SIGINT, lambda: loop.create_task(application.close()))
    loop.add_signal_handler(signal.SIGQUIT, lambda: loop.create_task(application.close()))
    loop.add_signal_handler(signal.SIGTERM, lambda: loop.create_task(application.close()))


if __name__ == "__main__":
    main_loop = asyncio.new_event_loop()
    start(Application(), Config(), main_loop)
    main_loop.run_forever()
