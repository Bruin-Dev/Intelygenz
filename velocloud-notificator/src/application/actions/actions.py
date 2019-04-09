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
        self._slack_repository.send_to_slack(msg)

    def store_stats(self, msg):
        self._statistic_repository.send_to_stats_client(msg)
