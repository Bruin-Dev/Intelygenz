import sys
from prometheus_client import start_http_server
from dependency_injector.wiring import inject, Provide
from adapters.config import settings
from containers import Application
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


@inject
def main(http_server=Provide[Application.delivery.http_server]) -> None:
    http_server.start()


def start_prometheus_metrics_server():
    start_http_server(settings.METRICS_SERVER_CONFIG['port'])


if __name__ == "__main__":
    start_prometheus_metrics_server()

    application = Application()
    application.wire(modules=[sys.modules[__name__]])
    main()
