class Actions:

    _config = None
    _slack_repository = None
    _statistic_repository = None

    def __init__(self, config, slack_repository, statistic_repository):
        self._config = config
        self._slack_repository = slack_repository
        self._statistic_repository = statistic_repository

    def send_to_slack(self, msg):
        if getattr(self._slack_repository, 'send_to_slack') is None:
            print(f'The object {self._slack_repository} has no method named send_to_slack')
            return None
        self._slack_repository.send_to_slack(msg)

    # Sends msg to stats repo to get stored
    def store_stats(self, msg):
        if getattr(self._statistic_repository, 'send_to_stats_client') is None:
            print(f'The object {self._statistic_repository} has no method named send_to_stats_client')
            return None
        self._statistic_repository.send_to_stats_client(msg)
