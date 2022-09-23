import asyncio
import logging
import signal
from asyncio import AbstractEventLoop

from framework.logging.formatters import Papertrail as PapertrailFormatter
from framework.logging.formatters import Standard as StandardFormatter
from framework.logging.handlers import Papertrail as PapertrailHandler
from framework.logging.handlers import Stdout as StdoutHandler

from config.config import Config
from health_server import HealthServer

log = logging.getLogger("application")
log.setLevel(logging.DEBUG)


class Application:
    health_server: HealthServer

    async def start(self, config: Config):
        # Logging configuration
        stdout_handler = StdoutHandler()
        stdout_handler.setFormatter(StandardFormatter(environment_name=config.environment_name))
        log.addHandler(stdout_handler)

        if config.is_papertrail_active:
            papertrail_handler = PapertrailHandler(host=config.papertrail_host, port=config.papertrail_port)
            papertrail_handler.setFormatter(
                PapertrailFormatter(
                    environment_name=config.environment_name,
                    papertrail_prefix=config.papertrail_prefix,
                )
            )
            log.addHandler(papertrail_handler)

        log.info("Starting forticloud-monitor ...")
        log.info("==========================================================")

        # Health server
        log.info("Starting health server ...")
        self.health_server = HealthServer("health_server", 5000)
        await self.health_server.start(asyncio.get_running_loop())
        log.info("Health server started")

        log.info("==========================================================")
        log.info("Forticloud monitor started")

    async def close(self, stop_loop: bool = True):
        log.info("Closing Forticloud monitor ...")
        log.info("==========================================================")

        log.info("Closing health server ...")
        await self.health_server.close()
        log.info("Health server closed")

        if stop_loop:
            asyncio.get_running_loop().stop()
            log.info("Event loop stopped")

        log.info("==========================================================")
        log.info("Forticloud monitor closed")


def start(application: Application, config: Config, loop: AbstractEventLoop):
    loop.create_task(application.start(config))

    def close_application():
        loop.create_task(application.close())

    loop.add_signal_handler(signal.SIGINT, close_application)
    loop.add_signal_handler(signal.SIGQUIT, close_application)
    loop.add_signal_handler(signal.SIGTERM, close_application)


if __name__ == "__main__":
    main_loop = asyncio.new_event_loop()
    start(Application(), Config(), main_loop)
    main_loop.run_forever()
