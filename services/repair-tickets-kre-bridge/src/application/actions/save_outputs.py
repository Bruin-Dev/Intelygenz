import json


class SaveOutputs:

    def __init__(self, logger, config, event_bus, repository):
        self._config = config
        self._logger = logger
        self._event_bus = event_bus
        self._kre_repository = repository

    async def save_outputs(self, msg: dict):
        """Call KRE workflow to store validationa and ticket creation outputs.

        Args:
            msg (dict): The request.
        """
        request_id = msg['request_id']
        response_topic = msg['response_topic']
        response = {
            'request_id': request_id,
            'body': None,
            'status': None
        }

        msg_body = msg.get('body')
        if not msg_body:
            self._logger.error(f'Cannot post automation outputs using {json.dumps(msg)}. JSON malformed')
            response['body'] = 'You must specify body in the request'
            response['status'] = 400
            await self._event_bus.publish_message(response_topic, response)
            return

        post_outputs_response = await self._kre_repository.save_outputs(msg_body)
        response = {
            'request_id': msg['request_id'],
            'body': post_outputs_response["body"],
            'status': post_outputs_response["status"]
        }

        await self._event_bus.publish_message(msg['response_topic'], response)
        self._logger.info(f'Save outputs response for email {msg_body["email_id"]} published in event bus!')
