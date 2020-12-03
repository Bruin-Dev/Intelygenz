from typing import Callable
from collections import defaultdict


class HawkeyeRepository:

    def __init__(self, logger, hawkeye_client, config):
        self._config = config
        self._logger = logger
        self._hawkeye_client = hawkeye_client

    async def get_probes(self, params):
        return await self.__make_paginated_request(self._hawkeye_client.get_probes, params)

    async def get_all_test(self, probes_id):
        result = {
            'body': [],
            'status': 200,
        }
        all_test_response = await self.__make_paginated_request(self._hawkeye_client.get_tests, {})

        if all_test_response['status'] not in range(200, 300):
            self._logger.error(f'Error when calling get_tests.')
            return all_test_response
        id_test_dict = defaultdict(lambda: [])
        for test in all_test_response['body']:
            if test['probeFromId'] in probes_id:
                id_test_dict[test['probeFromId']].append(test['id'])
            if test['probeToId'] in probes_id:
                id_test_dict[test['probeToId']].append(test['id'])
        if len(id_test_dict.keys()) <= 0:
            self._logger.error(f'Not find test for this probe ids.')
            return
        all_test_results_response = await self.__make_paginated_request(self._hawkeye_client.get_tests_results,
                                                                        {'timeInterval': 'Last15Min'})
        if all_test_results_response['status'] not in range(200, 300):
            self._logger.error(f'Error when calling get_tests_results.')
            return all_test_results_response

        result_details_with_probe = defaultdict(lambda: [])
        for probe_id in id_test_dict.keys():
            for test_result in all_test_results_response['body']:
                if test_result['testId'] in id_test_dict[probe_id]:
                    response_details = await self._hawkeye_client.get_test_result_details(test_result['tdrId'])
                    if response_details['status'] not in range(200, 300):
                        self._logger.error(f'Error when calling get_tests_results_details.')
                        return response_details
                    result_details_with_probe[probe_id].append(response_details['body'])
        result['body'] = result_details_with_probe
        return result

    async def __make_paginated_request(self, hawkclient: Callable, params):
        result = {
            'body': [],
            'status': 200,
        }
        retries = 0
        has_more = True
        offset = 0
        limit = 500
        params['limit'] = limit
        self._logger.info(f'Check all pages')
        while has_more:
            params['offset'] = offset
            response = await hawkclient(params)
            if response['status'] not in range(200, 300):
                if retries < self._config.HAWKEYE_CONFIG["retries"]:
                    retries += 1
                    continue
                self._logger.error(f'There have been 5 or more errors when do the paginated call. '
                                   f'The values obtained so far will be returned')
                return result
            retries = 0
            result['body'] += response['body']['records']
            offset += limit
            has_more = bool(response['body']['has_more'])
        return result
