class GetPrediction:

    def __init__(self, logger, config, event_bus, t7_repository):
        self._config = config
        self._logger = logger
        self._event_bus = event_bus
        self._t7_repository = t7_repository

    async def get_prediction(self, msg: dict):
        if msg.get('ticket_id'):
            ticket_id = msg["ticket_id"]
            prediction = self._t7_repository.get_prediction(ticket_id)
            response = {
                'request_id': msg['request_id'],
                'prediction': prediction["body"],
                'status': prediction["status_code"]
            }
            self._logger.info(f'Sending prediction for ticketID: {ticket_id}...')
        else:
            response = {
                'request_id': msg['request_id'],
                'prediction': "You must specify a ticket_id in order to get a prediction",
                'status': 400
            }
            self._logger.error(f'Ticket id not specified for : {msg["request_id"]}')

        await self._event_bus.publish_message(msg['response_topic'], response)
        self._logger.info(f'Message published in event bus')
