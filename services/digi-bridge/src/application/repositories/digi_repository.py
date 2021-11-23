from datetime import datetime

from apscheduler.util import undefined
from pytz import timezone


class DiGiRepository:

    def __init__(self, config, logger, scheduler, digi_client):
        self._config = config
        self._logger = logger
        self._scheduler = scheduler
        self._digi_client = digi_client

    async def login_job(self, exec_on_start=False):
        self._logger.info('Scheduled task: logging in digi api')
        next_run_time = undefined
        if exec_on_start:
            next_run_time = datetime.now(timezone(self._config.DIGI_CONFIG['timezone']))
            self._logger.info(f'It will be executed now')
        self._scheduler.add_job(self._digi_client.login, 'interval',
                                minutes=self._config.DIGI_CONFIG['login_ttl'],
                                next_run_time=next_run_time, replace_existing=True,
                                id='login')

    async def reboot(self, payload):
        return await self._digi_client.reboot(payload)

    async def get_digi_recovery_logs(self, payload):
        return await self._digi_client.get_digi_recovery_logs(payload)
