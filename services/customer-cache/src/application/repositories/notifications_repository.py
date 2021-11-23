from shortuuid import uuid


class NotificationsRepository:
    def __init__(self, event_bus, config):
        self._event_bus = event_bus
        self._config = config

    async def send_slack_message(self, message: str):
        message = {
            'request_id': uuid(),
            'message': f'[{self._config.LOG_CONFIG["name"]}] {message}',
        }
        await self._event_bus.rpc_request("notification.slack.request", message, timeout=10)

    async def send_email(self, email_object: dict):
        await self._event_bus.rpc_request("notification.email.request", email_object, timeout=60)
