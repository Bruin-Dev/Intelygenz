
class Actions:

    _config = None
    _slack_repository = None

    def __init__(self, config, slack_repository):
        self._config = config
        self._slack_repository = slack_repository

    def base_notification(self, msg):
        self._slack_repository.send_to_slack(msg)
