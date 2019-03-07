class Actions:

    _config = None
    _slack_repository = None
    _statistic_repository = None

    def __init__(self, config, slack_repository, statistic_repository):
        self._config = config
        self._slack_repository = slack_repository
        self._statistic_repository = statistic_repository

    def base_notification(self, msg):
        self._slack_repository.send_to_slack(msg)

    # Sends msg to stats repo to get stored
    def store_stats(self, msg):
        self._statistic_repository.send_to_stats_client(msg)
