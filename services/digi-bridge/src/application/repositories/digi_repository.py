import logging
from datetime import datetime

from pytz import timezone

logger = logging.getLogger(__name__)


class DiGiRepository:
    def __init__(self, config, scheduler, digi_client):
        self.config = config
        self._scheduler = scheduler
        self._digi_client = digi_client

    async def login_job(self):
        logger.info("Scheduled task: logging in digi api")
        self._scheduler.add_job(
            self._digi_client.login,
            "interval",
            minutes=self.config.DIGI_CONFIG["login_ttl"],
            next_run_time=datetime.now(timezone(self.config.TIMEZONE)),
            replace_existing=True,
            id="login",
        )

    async def reboot(self, request_filters):
        return await self._digi_client.reboot(request_filters)

    async def get_digi_recovery_logs(self, request_filters):
        return await self._digi_client.get_digi_recovery_logs(request_filters)
