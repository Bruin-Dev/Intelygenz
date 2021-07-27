import asyncio
from igz.packages.Logger.logger_client import LoggerClient

from application.actions.get_link_metrics import GetLinkMetrics
from application.clients.mongo_client import MyMongoClient
from application.server.api_server import APIServer
from config import config


class Container:

    def __init__(self):
        # LOGGER
        self._logger = LoggerClient(config).get_logger()
        self._logger.info(f'Links metrics API starting in: {config.CURRENT_ENVIRONMENT}...')

        # CLIENTS
        self._mongo_client = MyMongoClient(logger=self._logger, config=config)

        self._get_links_metrics = GetLinkMetrics(self._logger, config, self._mongo_client)

        # API
        self._api_server = APIServer(self._logger, config, self._get_links_metrics)

    async def start_server(self):
        await self._api_server.run_server()


if __name__ == '__main__':
    container = Container()
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(container.start_server(), loop=loop)
    loop.run_forever()
