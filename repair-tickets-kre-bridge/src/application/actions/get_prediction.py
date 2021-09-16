import json


class GetPrediction:

    def __init__(self, logger, config, event_bus, repository):
        self._config = config
        self._logger = logger
        self._event_bus = event_bus
        self._kre_repository = repository

    async def get_prediction(self, msg: dict):
        """Get the prediction from the KRE process and publish it.

        TODO: This is a scaffold, add real logic.

        Args:
            msg (dict): The request.
        """
        msg_body = msg["body"]
        email_id = msg_body["email"]

        prediction = await self._kre_repository.get_prediction(msg_body)

        response = {
            'request_id': msg['request_id'],
            'body': prediction["body"],
            'status': prediction["status"]
        }

        await self._event_bus.publish_message(msg['response_topic'], response)
        self._logger.info(f'Prediction for email {email_id} published in event bus!')
