import asyncio
import re
import time

from datetime import datetime
from datetime import timedelta
from typing import Set

from apscheduler.util import undefined
from dateutil.parser import parse
from pytz import timezone
from pytz import utc
from tenacity import retry, wait_exponential, stop_after_delay

from igz.packages.eventbus.eventbus import EventBus


class TicketsReports:
    __triage_note_regex = re.compile(r'#\*Automation Engine\*#\nTriage \(VeloCloud\)')

    def __init__(self, logger, scheduler, config,  tickets_cache_repository):
        self._logger = logger
        self._scheduler = scheduler
        self._config = config
        self._tickets_cache_repository = tickets_cache_repository

    async def start_job(self):
        self._logger.info(f'Scheduled task: service tickets reports configured to run every '
                          f'{self._config.TICKETS_REPORTS["polling_minutes"]} minutes')

        self._scheduler.add_job(self._run_tickets_polling, 'interval',
                                minutes=self._config.TICKETS_REPORTS["polling_minutes"],
                                replace_existing=True, id='_tickets_reports_process')

    async def _run_tickets_polling(self):
        self._logger.info(f'Starting tickets reports process...')
        self._logger.info('Getting all tickets...')
        tickets = await self.get_all_tickets()
        self._logger.info(tickets)

    def get_all_tickets(self):
        return self._tickets_cache_repository.get_cache()
