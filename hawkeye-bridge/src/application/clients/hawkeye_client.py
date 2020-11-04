import aiohttp


class HawkeyeClient:
    def __init__(self, logger, config):
        self._config = config
        self._logger = logger

        self._session = aiohttp.ClientSession()

    async def login(self):
        result = dict.fromkeys(["body", "status"])

        request_body = {
            'username': self._config.HAWKEYE_CONFIG['client_username'],
            'password': self._config.HAWKEYE_CONFIG['client_password'],
        }

        try:
            self._logger.info('Login into Hawkeye...')

            response = await self._session.post(
                f"{self._config.HAWKEYE_CONFIG['base_url']}/login",
                json=request_body,
                ssl=True,
            )
        except aiohttp.ClientConnectionError:
            result["body"] = 'Error while connecting to Hawkeye API'
            result["status"] = 500
            self.__log_result(result)
            return result

        if response.status == 401:
            result["body"] = "Username doesn't exist or password is incorrect"
            result["status"] = response.status
            self.__log_result(result)
            return result

        if response.status in range(500, 513):
            result["body"] = "Got internal error from Hawkeye"
            result["status"] = 500
            self.__log_result(result)
            return result

        self._logger.info('Logged into Hawkeye!')

        self._logger.info('Loading authentication cookie into the cookie jar...')
        # This step is automatically handled by aiohttp internally, but just to make sure...
        self._session.cookie_jar.update_cookies(response.cookies)

        result['body'] = await response.json()
        result['status'] = response.status

        return result

    def __log_result(self, result: dict):
        body, status = result['body'], result['status']

        if status == 400:
            self._logger.error(f"Got error from Hawkeye -> {body}")
        if status == 401:
            self._logger.error(f'Authentication error -> {body}')
        if status in range(500, 513):
            self._logger.error(f"Got {status} from Hawkeye")
