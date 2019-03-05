
class SlackRepository:

    _config = None
    _slack_client = None

    def __init__(self, config, slack_client):
        self._config = config
        self._slack_client = slack_client

    def send_to_slack(self, msg):
        # Converts message to format that can be dumped by json
        # in the slack_client
        # Does this here becuase the Slack Repo should be doing
        # the msg transformations
        slack_msg = {'text': str(msg)}
        self._slack_client.send_to_slack(slack_msg)
