from igz.packages.eventbus.eventbus import EventBus


class SendToSms:

    def __init__(self, config, event_bus: EventBus, logger, telestax_repository):
        self._config = config
        self._event_bus = event_bus
        self._logger = logger
        self._telestax_repository = telestax_repository

    async def send_to_sms(self, msg: dict):
        status = 400
        msg_body = msg.get('body')
        if msg_body is not None \
                and "sms_data" in msg_body and msg_body["sms_data"] is not None and msg_body["sms_data"] != "" \
                and "sms_to" in msg_body and msg_body["sms_to"] is not None and msg_body["sms_to"] != []:
            status = self._telestax_repository.send_to_sms(msg_body["sms_data"], msg_body["sms_to"])
        notification_response = {"request_id": msg['request_id'], "status": status}
        await self._event_bus.publish_message(msg["response_topic"], notification_response)
