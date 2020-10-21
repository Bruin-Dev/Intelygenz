missing = object()


class LinksMetricInfo:
    def __init__(self, event_bus, logger, velocloud_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._velocloud_repository = velocloud_repository

    async def get_links_metric_info(self, request: dict):
        request_id = request['request_id']
        response_topic = request['response_topic']

        response = {
            'request_id': request_id,
            'body': None,
            'status': None,
        }

        request_body: dict = request.get('body', missing)
        if request_body is missing:
            self._logger.error(f'Cannot get links metric info: "body" is missing in the request')
            response['body'] = 'Must include "body" in the request'
            response['status'] = 400
            await self._event_bus.publish_message(response_topic, response)
            return

        velocloud_host: str = request_body.get('host', missing)
        if velocloud_host is missing:
            self._logger.error(f'Cannot get links metric info: "host" is missing in the body of the request')
            response['body'] = 'Must include "host" and "interval" in the body of the request'
            response['status'] = 400
            await self._event_bus.publish_message(response_topic, response)
            return

        interval: str = request_body.get('interval', missing)
        if interval is missing:
            self._logger.error(f'Cannot get links metric info: "interval" is missing in the body of the request')
            response['body'] = 'Must include "host" and "interval" in the body of the request'
            response['status'] = 400
            await self._event_bus.publish_message(response_topic, response)
            return

        self._logger.info(f'Getting links metric info from Velocloud host "{velocloud_host}"...')
        links_metric_info_response: dict = await self._velocloud_repository.get_links_metric_info(
            velocloud_host, interval
        )

        response = {
            'request_id': request_id,
            **links_metric_info_response,
        }
        await self._event_bus.publish_message(response_topic, response)
        self._logger.info(f'Published links metric info in the event bus for request {request}')
