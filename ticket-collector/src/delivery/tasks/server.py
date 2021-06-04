import abc
import time
import datetime
import asyncio

from delivery.tasks import get_data_tasks
from igz.packages.server.api import QuartServer
from adapters.config import settings


class ITasksServer(metaclass=abc.ABCMeta):

    def __init__(self, config, logger, use_cases) -> None:
        from apscheduler.schedulers.background import BackgroundScheduler

        self.config = config
        self.logger = logger
        self.use_cases = use_cases
        self.scheduler = BackgroundScheduler()
        self.use_cases.wire(modules=[get_data_tasks])
        self._server = QuartServer(settings)
        self.initialize()

    @abc.abstractmethod
    def status(self):
        pass


class TasksServer(ITasksServer):
    JOB_ID = 'TICKET_COLLECTOR_JOB'
    START_HOUR = 22
    END_HOUR = 4

    def initialize(self):
        self.logger.info("Init tasks server")
        self.scheduler.add_job(get_data_tasks.get_data, 'cron',
                               max_instances=1,
                               hour=f'{self.START_HOUR}',
                               id=self.JOB_ID)

    async def start(self):
        self.logger.info("Starting server")
        self.scheduler.start()

        while True:
            await asyncio.sleep(60)
            now = datetime.datetime.now()
            job = self.scheduler.get_job(job_id=self.JOB_ID)

            self.logger.info(f'Checking job {self.JOB_ID}')

            if self.START_HOUR <= self.END_HOUR:
                if self.START_HOUR <= now.hour <= self.END_HOUR:
                    self.logger.info(f'Resume job {self.JOB_ID} at hour {now.hour}')
                    self.scheduler.resume()
                else:
                    self.logger.info(f'Pausing job {self.JOB_ID} at hour {now.hour}')
                    self.scheduler.pause()
            else:
                if self.START_HOUR <= now.hour or now.hour <= self.END_HOUR:
                    self.logger.info(f'Resume job {self.JOB_ID} at hour {now.hour}')
                    self.scheduler.resume()
                else:
                    self.logger.info(f'Pausing job {self.JOB_ID} at hour {now.hour}')
                    self.scheduler.pause()

    async def health(self):
        self.logger.info("Starting health check endpoint")
        await self._server.run_server()

    def status(self):
        self.logger.info("Tasks server is up")
