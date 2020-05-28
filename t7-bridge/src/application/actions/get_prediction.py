import json


class GetPrediction:

    def __init__(self, logger, config, event_bus, t7_repository):
        self._config = config
        self._logger = logger
        self._event_bus = event_bus
        self._t7_repository = t7_repository

    async def get_prediction(self, msg: dict):
        request_id = msg['request_id']
        response_topic = msg['response_topic']
        response = {
            'request_id': request_id,
            'body': None,
            'status': None
        }

        msg_body = msg.get('body')
        if not msg_body:
            self._logger.error(f'Cannot get prediction using {json.dumps(msg)}. JSON malformed')
            response['body'] = 'You must specify {.."body": {"ticket_id"}..} in the request'
            response['status'] = 400
            await self._event_bus.publish_message(response_topic, response)
            return

        ticket_id = msg_body.get('ticket_id')
        if not ticket_id:
            self._logger.error(f'Cannot get prediction using {json.dumps(msg_body)}. Need parameter "ticket_id"')
            response["body"] = 'You must specify {.."body": {"ticket_id"}..} in the request'
            response["status"] = 400
            await self._event_bus.publish_message(response_topic, response)
            return

        prediction = self._t7_repository.get_prediction(ticket_id)
        response = {
            'request_id': msg['request_id'],
            'body': prediction["body"],
            'status': prediction["status"]
        }

        await self._event_bus.publish_message(msg['response_topic'], response)
        self._logger.info(f'Prediction for ticket {ticket_id} published in event bus!')
