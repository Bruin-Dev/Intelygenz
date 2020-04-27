from datetime import datetime

from apscheduler.util import undefined
from pytz import timezone


class CtsRepository:

    def __init__(self, cts_client, logger, scheduler, config):
        self._cts_client = cts_client
        self._logger = logger
        self._scheduler = scheduler
        self._config = config

    def login_job(self, exec_on_start=False):
        self._logger.info(f'Scheduled task: logging in cts api')
        next_run_time = undefined
        if exec_on_start:
            next_run_time = datetime.now(timezone(self._config.CTS_CONFIG['timezone']))
            self._logger.info(f'It will be executed now')
        self._scheduler.add_job(self._cts_client.login, 'interval',
                                minutes=self._config.CTS_CONFIG['login_ttl'],
                                next_run_time=next_run_time, replace_existing=True,
                                id='login')

    def create_dispatch(self, payload):
        response = self._cts_client.create_dispatch(payload)
        return response

    def get_dispatch(self, dispatch_id):
        response = self._cts_client.get_dispatch(dispatch_id)
        return response

    def get_all_dispatches(self):
        response = self._cts_client.get_all_dispatches()
        return response

    def update_dispatch(self, dispatch_id, payload):
        response = self._cts_client.update_dispatch(dispatch_id, payload)
        return response
