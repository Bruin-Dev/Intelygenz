import json


class GetPrediction:

    def __init__(self, logger, config, event_bus, t7_repository):
        self._config = config
        self._logger = logger
        self._event_bus = event_bus
        self._t7_repository = t7_repository

    async def get_prediction(self, msg):
        msg_dict = json.loads(msg)
        ticket_id = msg_dict["ticket_id"]
        status = 500
        prediction = self._t7_repository.get_prediction(ticket_id)
        if prediction is not None:
            status = 200
        response = {
            'request_id': msg_dict['request_id'],
            'prediction': prediction,
            'status': status
        }
        await self._event_bus.publish_message(msg_dict['response_topic'],
                                              json.dumps(response, default=str))
        self._logger.info(f'prediction for ticketID: {ticket_id} sent!')
