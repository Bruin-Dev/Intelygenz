import abc
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from delivery.tasks import get_data_tasks
from igz.packages.server.api import QuartServer

from adapters.config import settings


class ITasksServer(metaclass=abc.ABCMeta):
    def __init__(self, config, logger, use_cases) -> None:
        self.config = config
        self.logger = logger
        self.use_cases = use_cases
        self.scheduler = AsyncIOScheduler()
        self.use_cases.wire(modules=[get_data_tasks])
        self._server = QuartServer(settings)
        self.initialize()

    @abc.abstractmethod
    def status(self):
        pass


class TasksServer(ITasksServer):
    def initialize(self):
        self.logger.info('Adding job to scheduler')
        self.scheduler.add_job(get_data_tasks.get_data, 'interval',
                               hours=self.config['job_interval_hours'],
                               next_run_time=datetime.now(),
                               replace_existing=False,
                               id='_ticket_collector_job')

    async def start(self):
        self.logger.info('Starting scheduler')
        self.scheduler.start()

    async def health(self):
        self.logger.info('Starting health check endpoint')
        await self._server.run_server()

    def status(self):
        self.logger.info('Tasks server is up')
