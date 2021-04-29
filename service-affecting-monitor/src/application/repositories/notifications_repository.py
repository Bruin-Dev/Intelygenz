from shortuuid import uuid


class NotificationsRepository:
    def __init__(self, event_bus):
        self._event_bus = event_bus

    async def send_slack_message(self, message: str):
        message = {
            'request_id': uuid(),
            'message': message,
        }
        await self._event_bus.rpc_request("notification.slack.request", message, timeout=10)

    async def send_email(self, email_object: dict):
        await self._event_bus.rpc_request("notification.email.request", email_object, timeout=60)

    async def notify_successful_ticket_forward(self, ticket_id: int, serial_number: str):
        message = (
            f'Detail related to serial {serial_number} in ticket {ticket_id} was successfully forwarded '
            'to the HNOC queue'
        )
        await self.send_slack_message(message)
