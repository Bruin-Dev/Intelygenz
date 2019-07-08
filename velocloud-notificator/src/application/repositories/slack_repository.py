class SlackRepository:

    _config = None
    _slack_client = None
    _logger = None

    def __init__(self, config, slack_client, logger):
        self._config = config
        self._slack_client = slack_client
        self._logger = logger

    def send_to_slack(self, msg):
        slack_msg = {'text': str(msg)}
        return self._slack_client.send_to_slack(slack_msg)
