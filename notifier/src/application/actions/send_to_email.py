from igz.packages.eventbus.eventbus import EventBus
import json


class SendToEmail:

    def __init__(self, config, event_bus: EventBus, logger, email_repository):
        self._config = config
        self._event_bus = event_bus
        self._logger = logger
        self._email_repository = email_repository

    async def send_to_email(self, msg):
        msg_dict = json.loads(msg)
        status = 500
        if msg_dict["email_data"] is not None and msg_dict["email_data"] != "":
            status = self._email_repository.send_to_email(msg_dict["email_data"])
        notification_response = {"request_id": msg_dict['request_id'], "status": status}
        await self._event_bus.publish_message(msg_dict["response_topic"], json.dumps(notification_response))
