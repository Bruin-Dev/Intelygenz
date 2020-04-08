from datetime import datetime

from apscheduler.util import undefined
from pytz import timezone


class LitRepository:

    def __init__(self, lit_client, logger, scheduler, config):
        self._lit_client = lit_client
        self._logger = logger
        self._scheduler = scheduler
        self._config = config

    def login_job(self, exec_on_start=False):
        self._logger.info(f'Scheduled task: logging in lit api')
        next_run_time = undefined
        if exec_on_start:
            next_run_time = datetime.now(timezone(self._config.LIT_CONFIG['timezone']))
            self._logger.info(f'It will be executed now')
        self._scheduler.add_job(self._lit_client.login, 'interval',
                                minutes=self._config.LIT_CONFIG['login_ttl'],
                                next_run_time=next_run_time, replace_existing=True,
                                id='login')

    def create_dispatch(self, payload):
        response = self._lit_client.create_dispatch(payload)
        return response

    def get_dispatch(self, dispatch_number):
        response = self._lit_client.get_dispatch(dispatch_number)
        return response

    def update_dispatch(self, payload):
        response = self._lit_client.update_dispatch(payload)
        return response

    def upload_file(self, dispatch_number, payload, file_name, file_content_type):
        response = self._lit_client.upload_file(dispatch_number, payload, file_name, file_content_type)
        return response
