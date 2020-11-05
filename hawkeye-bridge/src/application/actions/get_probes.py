class GetProbes:

    def __init__(self, logger, config, event_bus, hawkeye_repository):
        self._config = config
        self._logger = logger
        self._event_bus = event_bus
        self._hawkeye_repository = hawkeye_repository

    async def get_probes(self, msg: dict):
        probes_response = {
            'request_id': msg['request_id'],
            'body': None,
            'status': None
        }
        filters = {}
        body = msg.get("body")

        if body is None:
            probes_response["status"] = 400
            probes_response["body"] = 'Must include "body" in request'
            await self._event_bus.publish_message(msg['response_topic'], probes_response)
            return

        if 'serial_number' in body:
            filters['serial_number'] = body['serial_number']
        if 'status' in body:
            filters['status'] = body['status']

        self._logger.info(f'Collecting all probes ...')

        filtered_probes = await self._hawkeye_repository.get_probes(filters)

        filtered_probes_response = {**probes_response, **filtered_probes}

        await self._event_bus.publish_message(msg['response_topic'], filtered_probes_response)
