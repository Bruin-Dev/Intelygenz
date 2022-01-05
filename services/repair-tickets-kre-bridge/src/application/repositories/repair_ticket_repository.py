
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

    async def save_outputs(self, output_data: dict) -> dict:
        """Perform the actual request to the KRE.

        Args:
            output_data: information of validation/tickets created.

        Returns:
            dict: Response from kre
        """
        response = await self._kre_client.save_outputs(output_data)

        if response['status'] not in range(200, 300):
            return response

        return {
            'status': response['status'],
            'body': response.get('body', {})
        }

    async def save_created_ticket_feedback(self, created_ticket_data: dict) -> dict:
        """Save the created ticket

        Args:
            created_ticket_data: feedback for the model.

        Returns:
            dict: Response from kre
        """
        response = await self._kre_client.save_created_ticket_feedback(created_ticket_data)

        if response['status'] not in range(200, 300):
            return response

        return {
            'status': response['status'],
            'body': response.get('body', {})
        }

    async def save_closed_ticket_feedback(self, closed_ticket_data: dict) -> dict:
        """Save the closed ticket

        Args:
            closed_ticket_data: feedback for the model.

        Returns:
            dict: Response from kre
        """
        response = await self._kre_client.save_closed_ticket_feedback(closed_ticket_data)

        if response['status'] not in range(200, 300):
            return response

        return {
            'status': response['status'],
            'body': response.get('body', {})
        }
