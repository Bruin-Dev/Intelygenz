from igz.packages.eventbus.eventbus import EventBus


class SendToSms:

    def __init__(self, config, event_bus: EventBus, logger, telestax_repository):
        self._config = config
        self._event_bus = event_bus
        self._logger = logger
        self._telestax_repository = telestax_repository

    async def send_to_sms(self, msg: dict):
        status = 500
        if msg["email_data"] is not None and msg["sms_data"] != "":
            status = self._telestax_repository.send_to_sms(msg["sms_data"])
        notification_response = {"request_id": msg['request_id'], "status": status}
        await self._event_bus.publish_message(msg["response_topic"], notification_response)
