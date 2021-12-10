
class RepairTicketRepository:

    def __init__(self, logger, kre_client):
        self._logger = logger
        self._kre_client = kre_client

    async def get_email_inference(self, email_data: dict) -> dict:
        """Perform the actual request to the KRE.

        Args:
            email_data (dict): The request to the KRE.

        Returns:
            dict: The response of the KRE.
        """
        response = await self._kre_client.get_email_inference(email_data)

        if response['status'] not in range(200, 300):
            return response

        return {
            'status': response['status'],
            'body': response.get('body', {})
        }

    async def save_outputs(self, email_data: dict, ticket_data: dict) -> dict:
        return await self._kre_client.save_outputs(email_data)
