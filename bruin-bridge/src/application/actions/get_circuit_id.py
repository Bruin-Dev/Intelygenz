import json


class GetCircuitID:

    def __init__(self, logger, event_bus, bruin_repository):
        self._logger = logger
        self._event_bus = event_bus
        self._bruin_repository = bruin_repository

    async def get_circuit_id(self, msg: dict):
        request_id = msg['request_id']
        response_topic = msg['response_topic']
        response = {
            'request_id': request_id,
            'body': None,
            'status': None
        }
        if "body" not in msg.keys():
            self._logger.error(f'Cannot get bruin client info using {json.dumps(msg)}. '
                               f'JSON malformed')
            response["status"] = 400
            response["body"] = 'You must specify ' \
                               '{.."body":{"circuit_id", "client_id"}...} in the request'
            await self._event_bus.publish_message(response_topic, response)
            return

        params = msg['body']

        if not all(key in params.keys() for key in ("circuit_id", "client_id")):
            self._logger.error(f'Cannot get bruin circuit id using {json.dumps(params)}. Need "circuit_id",'
                               f'and "client_id"')
            response["status"] = 400
            response["body"] = 'You must specify "circuit_id" and "client_id" in the body'
            await self._event_bus.publish_message(response_topic, response)
            return

        self._logger.info(
            f'Getting Bruin circuit ID with filters: {json.dumps(params)}'
        )

        client_info = await self._bruin_repository.get_circuit_id(params)

        response["body"] = client_info["body"]
        response["status"] = client_info["status"]

        await self._event_bus.publish_message(response_topic, response)
        self._logger.info(
            f'Bruin circuit ID published in event bus for request {json.dumps(msg)}. '
            f"Message published was {response}"
        )
