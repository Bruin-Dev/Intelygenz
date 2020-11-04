import aiohttp


class HawkeyeClient:
    def __init__(self, logger, config):
        self._config = config
        self._logger = logger

        self._session = aiohttp.ClientSession()

    async def login(self):
        self._logger.info('Logging into Hawkeye...')
        self._logger.info('Logged into Hawkeye!')
