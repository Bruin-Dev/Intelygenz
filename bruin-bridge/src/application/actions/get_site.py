import json


class GetSite:

    def __init__(self, logger, event_bus, bruin_repository):
        self._logger = logger
        self._event_bus = event_bus
        self._bruin_repository = bruin_repository

    async def get_site(self, msg: dict):
        request_id = msg['request_id']
        response_topic = msg['response_topic']
        response = {
            'request_id': request_id,
            'body': None,
            'status': None
        }
        if "body" not in msg.keys():
            self._logger.error(f'Cannot get bruin site using {json.dumps(msg)}. '
                               f'JSON malformed')
            response["status"] = 400
            response["body"] = 'You must specify ' \
                               '{.."body":{"client_id":...}} in the request'
            await self._event_bus.publish_message(response_topic, response)
            return

        filters = msg['body']

        if "client_id" not in filters.keys():
            self._logger.error(f'Cannot get bruin site using {json.dumps(filters)}. Need "client_id"')
            response["status"] = 400
            response["body"] = 'You must specify "client_id" in the body'
            await self._event_bus.publish_message(response_topic, response)
            return

        self._logger.info(
            f'Getting Bruin site with filters: {json.dumps(filters)}'
        )

        site = await self._bruin_repository.get_site(filters)

        response["body"] = site["body"]
        response["status"] = site["status"]

        await self._event_bus.publish_message(response_topic, response)
        self._logger.info(
            f'Bruin get_site published in event bus for request {json.dumps(msg)}. '
            f"Message published was {response}"
        )
