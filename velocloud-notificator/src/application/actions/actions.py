import asyncio


class Actions:
    _config = None
    _slack_repository = None
    _statistic_repository = None
    _logger = None

    def __init__(self, config, slack_repository, statistic_repository, logger, scheduler):
        self._config = config
        self._slack_repository = slack_repository
        self._statistic_repository = statistic_repository
        self._logger = logger
        self._scheduler = scheduler

    def send_to_slack(self, msg):
        self._slack_repository.send_to_slack(msg)

    def store_stats(self, msg):
        self._statistic_repository.send_to_stats_client(msg)

    def set_stats_to_slack_job(self):
        seconds = self._config.SLACK_CONFIG['time']
        self._scheduler.add_job(self._stats_to_slack_job, 'interval', seconds=seconds)

    def _stats_to_slack_job(self):
        time = self._config.SLACK_CONFIG['time']
        sec_to_min = time / 60
        msg = self._statistic_repository._statistic_client.get_statistics(sec_to_min)
        if msg is not None:
            self.send_to_slack(msg)
        self._statistic_repository._statistic_client.clear_dictionaries()
        self._logger.info(f'{sec_to_min} minutes has passed')
