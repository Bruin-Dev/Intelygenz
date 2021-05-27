import abc
import time
from delivery.tasks import get_data_tasks


class ITasksServer(metaclass=abc.ABCMeta):

    def __init__(self, config, logger, use_cases) -> None:
        from apscheduler.schedulers.background import BackgroundScheduler

        self.config = config
        self.logger = logger
        self.use_cases = use_cases
        self.scheduler = BackgroundScheduler()
        self.use_cases.wire(modules=[get_data_tasks])
        self.initialize()

    @abc.abstractmethod
    def status(self):
        pass


class TasksServer(ITasksServer):
    def initialize(self):
        self.logger.info("Init tasks server")

        self.scheduler.add_job(get_data_tasks.get_data, 'interval',
                               max_instances=1,
                               hours=22-6,)

    def start(self):
        self.logger.info("Starting server")
        self.scheduler.start()

        while True:
            time.sleep(2)

    def status(self):
        self.logger.info("Tasks server is up")
