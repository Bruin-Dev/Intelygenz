from igz.packages.eventbus.eventbus import EventBus


class SendToEmail:
    def __init__(self, config, event_bus: EventBus, logger, email_repository):
        self._config = config
        self._event_bus = event_bus
        self._logger = logger
        self._email_repository = email_repository

    async def send_to_email(self, msg: dict):
        status = 500
        if msg["email_data"] is not None and msg["email_data"] != "":
            status = self._email_repository.send_to_email(msg["email_data"])
        notification_response = {"request_id": msg["request_id"], "status": status}
        await self._event_bus.publish_message(msg["response_topic"], notification_response)
