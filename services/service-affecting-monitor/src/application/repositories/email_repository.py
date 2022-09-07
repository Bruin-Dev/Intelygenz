class EmailRepository:
    def __init__(self, event_bus):
        self._event_bus = event_bus

    async def send_email(self, email_object: dict):
        await self._event_bus.rpc_request("notification.email.request", email_object, timeout=60)
