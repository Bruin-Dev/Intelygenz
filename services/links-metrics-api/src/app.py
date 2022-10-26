import asyncio
import logging

from framework.logging.formatters import Papertrail as PapertrailFormatter
from framework.logging.formatters import Standard as StandardFormatter
from framework.logging.handlers import Papertrail as PapertrailHandler
from framework.logging.handlers import Stdout as StdoutHandler
from prometheus_client import start_http_server

from application.actions.get_link_metrics import GetLinkMetrics
from application.clients.mongo_client import MyMongoClient
from application.server.api_server import APIServer
from config import config

# Standard output logging
base_handler = StdoutHandler()
base_handler.setFormatter(StandardFormatter(environment_name=config.ENVIRONMENT_NAME))

app_logger = logging.getLogger("application")
app_logger.setLevel(logging.DEBUG)
app_logger.addHandler(base_handler)

framework_logger = logging.getLogger("framework")
framework_logger.setLevel(logging.DEBUG)
framework_logger.addHandler(base_handler)

# Papertrail logging
if config.LOG_CONFIG["papertrail"]["active"]:
    pt_handler = PapertrailHandler(
        host=config.LOG_CONFIG["papertrail"]["host"],
        port=config.LOG_CONFIG["papertrail"]["port"],
    )
    pt_handler.setFormatter(
        PapertrailFormatter(
            environment_name=config.ENVIRONMENT_NAME,
            papertrail_prefix=config.LOG_CONFIG["papertrail"]["prefix"],
        )
    )
    app_logger.addHandler(pt_handler)
    framework_logger.addHandler(pt_handler)

# APScheduler logging
apscheduler_logger = logging.getLogger("apscheduler")
apscheduler_logger.setLevel(logging.DEBUG)
apscheduler_logger.addHandler(base_handler)


class Container:
    def __init__(self):
        # LOGGER
        app_logger.info(f"Links metrics API starting in: {config.CURRENT_ENVIRONMENT}...")

        # CLIENTS
        self._mongo_client = MyMongoClient(config=config)

        # ACTIONS
        self._get_links_metrics = GetLinkMetrics(config, self._mongo_client)

        # API
        self._api_server = APIServer(config, self._get_links_metrics)

    async def run(self):
        # Prometheus
        self._start_prometheus_metrics_server()

        await self._mongo_client.create_connection()

        await self._api_server.run_server()

    @staticmethod
    def _start_prometheus_metrics_server():
        start_http_server(config.METRICS_SERVER_CONFIG["port"])


if __name__ == "__main__":
    container = Container()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    asyncio.ensure_future(container.run(), loop=loop)

    loop.run_forever()
