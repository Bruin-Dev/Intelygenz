class EmailTaggerRepository:
    def __init__(self, logger, kre_client):
        self._logger = logger
        self._kre_client = kre_client

    async def get_prediction(self, email_data: dict) -> dict:
        response = await self._kre_client.get_prediction(email_data)

        if response["status"] not in range(200, 300):
            return response

        return {"status": response["status"], "body": response.get("body", {}).get("prediction")}

    async def save_metrics(self, email_data: dict, ticket_data: dict) -> dict:
        return await self._kre_client.save_metrics(email_data, ticket_data)
