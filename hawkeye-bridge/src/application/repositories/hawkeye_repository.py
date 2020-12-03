from typing import Callable


class HawkeyeRepository:

    def __init__(self, logger, hawkeye_client, config):
        self._config = config
        self._logger = logger
        self._hawkeye_client = hawkeye_client

    async def get_probes(self, params):
        return await self.__make_paginated_request(self._hawkeye_client.get_probes, params)

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
                self._logger.error(f'There have been 5 or more errors when calling get_probes. '
                                   f'The values obtained so far will be returned')
                return result
            retries = 0
            result['body'] += response['body']['records']
            offset += limit
            has_more = bool(response['body']['has_more'])
        return result
