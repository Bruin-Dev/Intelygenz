from apscheduler.triggers.cron import CronTrigger
from pytz import timezone


class BandwidthReports:

    def __init__(self, logger, scheduler, config):
        self._logger = logger
        self._scheduler = scheduler
        self._config = config

    async def start_bandwidth_reports_job(self, exec_on_start=False):
        self._logger.info(f'Scheduled task: bandwidth reports')

        if exec_on_start:
            await self.bandwidth_reports()
        else:
            self._scheduler.add_job(self.bandwidth_reports,
                                    CronTrigger.from_crontab(self._config.BANDWIDTH_REPORT_CONFIG['crontab'],
                                                             timezone=timezone('UTC')),
                                    id='_bandwidth_reports', replace_existing=True)

    async def bandwidth_reports(self):
        pass
