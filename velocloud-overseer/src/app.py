from config import config
from igz.packages.nats.clients import NatsStreamingClient
from igz.packages.eventbus.eventbus import EventBus
from application.actions.actions import Actions
from application.repositories.velocloud_repository import VelocloudRepository
from igz.packages.Logger.logger_client import LoggerClient
import asyncio
from igz.packages.server.api import QuartServer
import socket


class Container:
    logger = None
    velocloud_repository = None
    publisher = None
    event_bus = None
    report_edge_action = None
    actions = None
    logger = LoggerClient(config).get_logger()
    server = QuartServer(config)

    def setup(self):
        self.velocloud_repository = VelocloudRepository(config, self.logger)

        self.publisher = NatsStreamingClient(config, "velocloud-overseer-publisher", logger=self.logger)
        self.event_bus = EventBus(logger=self.logger)
        self.event_bus.set_producer(self.publisher)

        self.actions = Actions(self.event_bus, self.velocloud_repository, self.logger)

    async def start(self):
        await self.event_bus.connect()
        await self.actions.send_edge_status_task_interval(config.OVERSEER_CONFIG['interval_time'], exec_on_start=True)

    async def start_server(self):
        await self.server.run_server()

    async def run(self):
        self.setup()
        await self.start()


def resolve_ns():
    container.logger.info('resolving \'%s\'' % config.NATS_CONFIG['servers'][7:-5])
    ip_list = []
    ais = socket.getaddrinfo(config.NATS_CONFIG['servers'][7:-5], 0, 0, 0, 0)
    for result in ais:
        ip_list.append(result[-1][0])
    ip_list = list(set(ip_list))
    container.logger.info(ip_list)


if __name__ == '__main__':
    container = Container()
    container.logger.info("Velocloud overseer starting...")
    resolve_ns()
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(container.run(), loop=loop)
    asyncio.ensure_future(container.start_server(), loop=loop)
    loop.run_forever()
