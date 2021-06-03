import sys
from dependency_injector.wiring import inject, Provide
from containers import Application
import urllib3
import asyncio

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


@inject
def main(tasks_server=Provide[Application.delivery.tasks_server]) -> None:
    futures = [tasks_server.start()]
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(futures))


if __name__ == "__main__":
    application = Application()
    application.wire(modules=[sys.modules[__name__]])
    main()
