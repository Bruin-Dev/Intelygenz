from datetime import datetime, timedelta
from typing import Callable
from collections import defaultdict


class HawkeyeRepository:

    def __init__(self, logger, hawkeye_client, config):
        self._config = config
        self._logger = logger
        self._hawkeye_client = hawkeye_client

    async def get_probes(self, params):
        return await self.__make_paginated_request(self._hawkeye_client.get_probes, params)

    async def get_test_results(self, probes_uids, interval):
        result = {
            'body': [],
            'status': 200,
        }
        test_results_by_probe_uid = defaultdict(lambda: [])
        for probe_uid in probes_uids:
            all_test_results_response = await self.__make_paginated_request(self._hawkeye_client.get_tests_results,
                                                                            {'startDate': interval['start'],
                                                                             'endDate': interval['end'],
                                                                             'limit': 100,
                                                                             'probeFrom': probe_uid})
            test_results_by_probe_uid[probe_uid] = all_test_results_response['body']

        result_details_with_probe = defaultdict(lambda: [])
        for probe_uid, tests_results in test_results_by_probe_uid.items():
            for test_result in tests_results:
                tdr_id = test_result['tdrId']
                response_details = await self._hawkeye_client.get_test_result_details(tdr_id)
                if response_details['status'] not in range(200, 300):
                    self._logger.error(f'Error when calling get_tests_results_details using TDR ID {tdr_id})')
                    continue
                result_details_with_probe[probe_uid].append(
                    {'summary': test_result, 'metrics': response_details['body']['metrics']})
        result['body'] = result_details_with_probe
        return result

    async def __make_paginated_request(self, fn: Callable, params: dict):
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
        self._logger.info(f'Fetching all pages using {fn.__name__}...')
        while has_more:
            params['offset'] = offset
            response = await fn(params)
            if response['status'] not in range(200, 300):
                if retries < self._config.HAWKEYE_CONFIG["retries"]:
                    retries += 1
                    continue
                self._logger.error(
                    f'There have been 5 or more errors when calling {fn.__name__}. ')
                return result
            retries = 0
            result['body'] += response['body']['records']
            offset += limit
            has_more = bool(response['body']['has_more'])
        return result
