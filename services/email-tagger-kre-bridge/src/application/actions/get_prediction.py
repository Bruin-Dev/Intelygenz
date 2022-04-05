import json


class GetPrediction:

    def __init__(self, logger, config, event_bus, repository):
        self._config = config
        self._logger = logger
        self._event_bus = event_bus
        self._kre_repository = repository

    async def get_prediction(self, msg: dict):
        request_id = msg['request_id']
        response_topic = msg['response_topic']
        response = {
            'request_id': request_id,
            'body': None,
            'status': None
        }

        err_body = 'You must specify {.."body": { "email": {"email_id", "subject", ...}}} in the request'
        msg_body = msg.get('body')
        if not msg_body:
            self._logger.error(f'Cannot get prediction using {json.dumps(msg)}. JSON malformed')
            response['body'] = err_body
            response['status'] = 400
            await self._event_bus.publish_message(response_topic, response)
            return

        email_data = msg_body.get('email')
        if not email_data:
            self._logger.error(
                f'Cannot get prediction using {json.dumps(msg_body)}. Need parameters "email"'
            )
            response["body"] = err_body
            response["status"] = 400
            await self._event_bus.publish_message(response_topic, response)
            return

        email_id = email_data.get('email_id')
        if not email_id:
            self._logger.error(
                f'Cannot get prediction using {json.dumps(msg_body)}. Need parameters "email_id"'
            )
            response["body"] = err_body
            response["status"] = 400
            await self._event_bus.publish_message(response_topic, response)
            return

        prediction = await self._kre_repository.get_prediction(msg_body)

        response = {
            'request_id': msg['request_id'],
            'body': prediction["body"],
            'status': prediction["status"]
        }

        await self._event_bus.publish_message(msg['response_topic'], response)
        self._logger.info(
            'request_id=%s, enail_id=%s Prediction %s published in event bus!',
            request_id,
            email_id,
            response
        )
