from igz.packages.eventbus.eventbus import EventBus


class SendToSlack:

    def __init__(self, config, event_bus: EventBus, slack_repository, logger):
        self._config = config
        self._event_bus = event_bus
        self._slack_repository = slack_repository
        self._logger = logger

    async def send_to_slack(self, msg: dict):
        status = self._slack_repository.send_to_slack(msg["message"])
        notification_response = {"request_id": msg["request_id"], "status": status}
        await self._event_bus.publish_message(msg["response_topic"], notification_response)
