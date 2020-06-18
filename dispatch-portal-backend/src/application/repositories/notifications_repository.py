from shortuuid import uuid


class NotificationsRepository:
    def __init__(self, event_bus):
        self._event_bus = event_bus

    async def send_email(self, email_object: dict):
        return await self._event_bus.rpc_request("notification.email.request", email_object, timeout=10)

    async def send_slack_message(self, message: str):
        message = {
            'request_id': uuid(),
            'message': message,
        }
        await self._event_bus.rpc_request("notification.slack.request", message, timeout=10)

    async def send_sms(self, payload: str):
        message = {
            'request_id': uuid(),
            'body': payload,
        }
        return await self._event_bus.rpc_request("notification.sms.request", message, timeout=10)
