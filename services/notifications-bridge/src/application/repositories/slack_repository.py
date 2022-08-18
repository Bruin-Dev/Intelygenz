class SlackRepository:
    _slack_client = None

    def __init__(self, slack_client):
        self._slack_client = slack_client

    async def send_to_slack(self, msg):
        slack_msg = {"text": str(msg)}
        return await self._slack_client.send_to_slack(slack_msg)
