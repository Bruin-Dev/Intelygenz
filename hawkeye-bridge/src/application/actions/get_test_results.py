class GetTestResults:

    def __init__(self, logger, config, event_bus, hawkeye_repository):
        self._config = config
        self._logger = logger
        self._event_bus = event_bus
        self._hawkeye_repository = hawkeye_repository

    async def get_test_results(self, msg: dict):
        probes_response = {
            'request_id': msg['request_id'],
            'body': None,
            'status': None
        }
        body = msg.get("body")
        if body is None:
            probes_response["status"] = 400
            probes_response["body"] = 'Must include "body" in request'
            await self._event_bus.publish_message(msg['response_topic'], probes_response)
            return

        if 'probe_ids' not in body:
            probes_response["status"] = 400
            probes_response["body"] = 'Must include "probes_ids" in the body of the request'
            return
        probe_id_list = body['probe_ids']
        self._logger.info(f'Collecting all test results ...')

        filtered_tests = await self._hawkeye_repository.get_all_test(probe_id_list)

        filtered_tests_response = {**probes_response, **filtered_tests}

        await self._event_bus.publish_message(msg['response_topic'], filtered_tests_response)
