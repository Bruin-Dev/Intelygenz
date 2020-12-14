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

        if 'probe_uids' not in body:
            probes_response["status"] = 400
            probes_response["body"] = 'Must include "probe_uids" in the body of the request'
            await self._event_bus.publish_message(msg['response_topic'], probes_response)
            return
        if 'start_date' not in body or 'end_date' not in body:
            probes_response["status"] = 400
            probes_response["body"] = 'Must include "start_date" and "end_date" in the body of the request'
            await self._event_bus.publish_message(msg['response_topic'], probes_response)
            return
        self._logger.info(f'Collecting all test results ...')

        filtered_tests = await self._hawkeye_repository.get_test_results(body['probe_uids'], body['start_date'],
                                                                         body['end_date'])

        filtered_tests_response = {**probes_response, **filtered_tests}

        await self._event_bus.publish_message(msg['response_topic'], filtered_tests_response)
