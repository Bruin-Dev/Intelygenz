import sys
from dependency_injector.wiring import inject, Provide
from containers import Application
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


@inject
def main(http_server=Provide[Application.delivery.http_server]) -> None:
    http_server.start()


if __name__ == "__main__":
    application = Application()
    application.wire(modules=[sys.modules[__name__]])
    main()
