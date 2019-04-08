class Actions:
    _config = None
    _slack_repository = None
    _statistic_repository = None
    _logger = None

    def __init__(self, config, slack_repository, statistic_repository, logger):
        self._config = config
        self._slack_repository = slack_repository
        self._statistic_repository = statistic_repository
        self._logger = logger

    def send_to_slack(self, msg):
        if hasattr(self._slack_repository, 'send_to_slack') is False:
            self._logger.error(f'The object {self._slack_repository} has no method named send_to_slack')
            return None
        self._slack_repository.send_to_slack(msg)

    def store_stats(self, msg):
        if hasattr(self._statistic_repository, 'send_to_stats_client') is False:
            self._logger.error(f'The object {self._statistic_repository} has no method named send_to_stats_client')
            return None
        self._statistic_repository.send_to_stats_client(msg)
