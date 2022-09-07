from shortuuid import uuid


class NotificationsRepository:
    def __init__(self, event_bus):
        self._event_bus = event_bus

    async def send_slack_message(self, message: str):
        message = {
            "request_id": uuid(),
            "body": {"message": message},
        }
        await self._event_bus.rpc_request("notification.slack.request", message, timeout=10)
