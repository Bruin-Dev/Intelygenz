import logging

logger = logging.getLogger(__name__)


class RepairTicketRepository:
    def __init__(self, kre_client):
        self._kre_client = kre_client

    async def get_email_inference(self, email_data: dict) -> dict:
        response = await self._kre_client.get_email_inference(email_data)

        if response["status"] not in range(200, 300):
            return response

        return {"status": response["status"], "body": response.get("body", {})}

    async def save_outputs(self, output_data: dict) -> dict:
        response = await self._kre_client.save_outputs(output_data)

        if response["status"] not in range(200, 300):
            return response

        return {"status": response["status"], "body": response.get("body", {})}

    async def save_created_ticket_feedback(self, created_ticket_data: dict) -> dict:
        response = await self._kre_client.save_created_ticket_feedback(created_ticket_data)

        if response["status"] not in range(200, 300):
            return response

        return {"status": response["status"], "body": response.get("body", {})}

    async def save_closed_ticket_feedback(self, closed_ticket_data: dict) -> dict:
        response = await self._kre_client.save_closed_ticket_feedback(closed_ticket_data)

        if response["status"] not in range(200, 300):
            return response

        return {"status": response["status"], "body": response.get("body", {})}
