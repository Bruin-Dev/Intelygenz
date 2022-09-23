from shortuuid import uuid


class NotificationsRepository:
    def __init__(self, nats_client, config):
        self._nats_client = nats_client
        self._config = config

    async def send_slack_message(self, message: str):
        message = {
            "request_id": uuid(),
            "body": {"message": f"[{self._config.LOG_CONFIG['name']}]: {message}"},
        }
        await self._nats_client.rpc_request("notification.slack.request", message, timeout=10)
