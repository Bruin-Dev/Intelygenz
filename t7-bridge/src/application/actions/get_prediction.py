import json


class GetPrediction:

    def __init__(self, logger, config, event_bus, t7_repository, t7_kre_repository):
        self._config = config
        self._logger = logger
        self._event_bus = event_bus
        self._t7_repository = t7_repository
        self._t7_kre_repository = t7_kre_repository

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

        ticket_rows = msg_body.get('ticket_rows')
        if not ticket_rows:
            msg = f'Cannot get KRE prediction using {json.dumps(msg_body)}. Need parameter "ticket_rows"'
            self._logger.error(msg)
            return

        get_kre_prediction_response = self._t7_kre_repository.get_prediction(ticket_id, ticket_rows)

        if get_kre_prediction_response["status"] == 200:
            msg = (
                f"KRE get prediction for ticket {msg_body['ticket_id']}"
            )
            self._logger.info(msg)
        else:
            msg = (
                f"ERROR on KRE get prediction for ticket_id[{msg_body['ticket_id']}]:"
                f"Body: {get_kre_prediction_response['body']}, Status: {get_kre_prediction_response['status']}"
            )
            self._logger.error(msg)
