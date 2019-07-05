from igz.packages.eventbus.eventbus import EventBus
import json


class Actions:

    def __init__(self, config, event_bus: EventBus, slack_repository, logger, email_repository):
        self._config = config
        self._event_bus = event_bus
        self._slack_repository = slack_repository
        self._logger = logger
        self._email_repository = email_repository

    async def send_to_slack(self, msg):
        msg_dict = json.loads(msg)
        status = self._slack_repository.send_to_slack(msg_dict["message"])
        notification_response = {"request_id": msg_dict["request_id"], "status": status}
        await self._event_bus.publish_message(msg_dict["response_topic"], json.dumps(notification_response))

    async def send_to_email_job(self, msg):
        msg_dict = json.loads(msg)
        status = 500
        if msg_dict["email_data"] is not None and msg_dict["email_data"] != "":
            status = self._email_repository.send_to_email(msg_dict["email_data"])
        notification_response = {"request_id": msg_dict['request_id'], "status": status}
        await self._event_bus.publish_message(msg_dict["response_topic"], json.dumps(notification_response))
