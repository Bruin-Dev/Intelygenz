import asyncio
import sys

from adapters.config import settings
from containers import Application
from dependency_injector.wiring import Provide, inject
from prometheus_client import start_http_server


@inject
def main(tasks_server=Provide[Application.delivery.tasks_server]) -> None:
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(tasks_server.health(), loop=loop)
    asyncio.ensure_future(tasks_server.start(), loop=loop)
    loop.run_forever()


def start_prometheus_metrics_server():
    start_http_server(settings.METRICS_SERVER_CONFIG["port"])


if __name__ == "__main__":
    start_prometheus_metrics_server()

    application = Application()
    application.wire(modules=[sys.modules[__name__]])
    main()
