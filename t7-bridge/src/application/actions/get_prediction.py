class GetPrediction:

    def __init__(self, logger, config, event_bus, t7_repository):
        self._config = config
        self._logger = logger
        self._event_bus = event_bus
        self._t7_repository = t7_repository

    async def get_prediction(self, msg: dict):
        ticket_id = msg["ticket_id"]
        status = 500
        prediction = self._t7_repository.get_prediction(ticket_id)
        if prediction is not None:
            status = 200
        response = {
            'request_id': msg['request_id'],
            'prediction': prediction,
            'status': status
        }
        await self._event_bus.publish_message(msg['response_topic'], response)
        self._logger.info(f'prediction for ticketID: {ticket_id} sent!')
