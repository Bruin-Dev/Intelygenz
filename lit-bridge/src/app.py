import sys
import redis

from config import config
from application.clients.lit_client import LitClient
from application.repositories.lit_repository import LitRepository
from application.actions.create_dispatch import CreateDispatch

from igz.packages.eventbus.eventbus import EventBus
from igz.packages.eventbus.storage_managers import RedisStorageManager

from igz.packages.Logger.logger_client import LoggerClient
import asyncio
from igz.packages.server.api import QuartServer


class Container:

    def __init__(self):
        self._logger = LoggerClient(config).get_logger()
        self._logger.info("Lit bridge starting...")

        self._redis_client = redis.Redis(host=config.REDIS["host"], port=6379, decode_responses=True)
        self._redis_client.ping()

        self._lit_client = LitClient(self._logger, config)

        self._lit_repository = LitRepository(self._lit_client, self._logger, config)

        self._message_storage_manager = RedisStorageManager(self._logger, self._redis_client)

        # self._publisher = NATSClient(config, logger=self._logger)
        # self._subscriber_create_dispatch = NATSClient(config, logger=self._logger)
        # TODO: the others
        self._event_bus = EventBus(self._message_storage_manager, logger=self._logger)
        self._create_dispatch = CreateDispatch(self._logger, config.LIT_CONFIG, self._event_bus,
                                               self._lit_repository)
        self._server = QuartServer(config)
        self._server._quart_server.add_url_rule('/create-dispatch',
                                                None, self._lit_repository.create_dispatch, methods=['POST'])
        self._server._quart_server.add_url_rule('/get-dispatch/<dispatch_number>',
                                                None, self._lit_repository.get_dispatch, methods=['GET'])
        self._server._quart_server.add_url_rule('/update-dispatch/<dispatch_number>',
                                                None, self._lit_repository.update_dispatch, methods=['POST'])
        self._server._quart_server.add_url_rule('/upload-file-dispatch/<dispatch_number>',
                                                None, self._lit_repository.upload_file, methods=['POST'])

    async def start(self):
        await self._event_bus.connect()
        self._lit_client.login()

    async def start_server(self):
        await self._server.run_server()


if __name__ == '__main__':
    container = Container()
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    try:
        asyncio.ensure_future(container.start(), loop=loop)
        asyncio.ensure_future(container.start_server(), loop=loop)
        loop.run_forever()
    except KeyboardInterrupt:
        print("Closing by user KeyboardInterrupt")
        sys.exit(1)
    except Exception as ex:
        print(ex)
        sys.exit(2)
    finally:
        loop.close()
