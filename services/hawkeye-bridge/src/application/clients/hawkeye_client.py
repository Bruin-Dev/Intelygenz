import aiohttp


class HawkeyeClient:
    def __init__(self, logger, config):
        self._config = config
        self._logger = logger

        self._session = aiohttp.ClientSession()

    async def login(self):
        result = dict.fromkeys(["body", "status"])

        request_body = {
            "username": self._config.HAWKEYE_CONFIG["client_username"],
            "password": self._config.HAWKEYE_CONFIG["client_password"],
        }

        try:
            self._logger.info("Login into Hawkeye...")

            response = await self._session.post(
                f"{self._config.HAWKEYE_CONFIG['base_url']}/login",
                json=request_body,
                ssl=True,
            )
        except aiohttp.ClientConnectionError:
            result["body"] = "Error while connecting to Hawkeye API"
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

        self._logger.info("Logged into Hawkeye!")

        self._logger.info("Loading authentication cookie into the cookie jar...")
        # This step is automatically handled by aiohttp internally, but just to make sure...
        self._session.cookie_jar.update_cookies(response.cookies)

        result["body"] = await response.json()
        result["status"] = response.status

        return result

    async def get_probes(self, filters):
        async def _get_probes():
            nonlocal retries
            return_response = dict.fromkeys(["body", "status"])
            try:
                self._logger.info(f"Getting probes using filters {filters}...")
                response = await self._session.get(
                    f'{self._config.HAWKEYE_CONFIG["base_url"]}/probes',
                    params=filters,
                    ssl=True,
                )
            except Exception as e:
                return_response["body"] = "Error while connecting to Hawkeye API"
                return_response["status"] = 500
                self.__log_result(return_response)
                return return_response
            if response.status in range(200, 300):
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status

            if response.status == 401:
                await self.login()
                return_response["body"] = "Got 401 from Hawkeye"
                return_response["status"] = response.status
                self.__log_result(return_response)
                if retries >= self._config.HAWKEYE_CONFIG["retries"]:
                    self._logger.error(f"Maximum number of retries exceeded")
                    return return_response
                retries += 1
                return_response = await _get_probes()

            if response.status in range(500, 513):
                return_response["body"] = "Got internal error from Hawkeye"
                return_response["status"] = 500
                self.__log_result(return_response)
            return return_response

        retries = 0
        return await _get_probes()

    async def get_tests_results(self, filters):
        async def _get_tests_results():
            nonlocal retries
            return_response = dict.fromkeys(["body", "status"])
            try:
                self._logger.info(f"Getting test results using filters {filters}...")
                response = await self._session.get(
                    f'{self._config.HAWKEYE_CONFIG["base_url"]}/testsresults',
                    params=filters,
                    ssl=True,
                )
            except Exception as e:
                return_response["body"] = "Error while connecting to Hawkeye API"
                return_response["status"] = 500
                self.__log_result(return_response)
                return return_response
            if response.status in range(200, 300):
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status

            if response.status == 400:
                return_response["body"] = "Parameters or body were in an incorrect format"
                return_response["status"] = response.status
                self.__log_result(return_response)

            if response.status == 401:
                await self.login()
                return_response["body"] = "Got 401 from Hawkeye"
                return_response["status"] = response.status
                self.__log_result(return_response)
                if retries >= self._config.HAWKEYE_CONFIG["retries"]:
                    self._logger.error(f"Maximum number of retries exceeded")
                    return return_response
                retries += 1
                return_response = await _get_tests_results()

            if response.status in range(500, 513):
                return_response["body"] = "Got internal error from Hawkeye"
                return_response["status"] = 500
                self.__log_result(return_response)
            return return_response

        retries = 0
        return await _get_tests_results()

    async def get_test_result_details(self, test_result_id):
        async def _get_test_result_details():
            nonlocal retries
            return_response = dict.fromkeys(["body", "status"])
            try:
                self._logger.info(f"Getting details of test result {test_result_id}...")
                response = await self._session.get(
                    f'{self._config.HAWKEYE_CONFIG["base_url"]}/testsresults/{test_result_id}',
                    ssl=True,
                )
            except Exception as e:
                return_response["body"] = "Error while connecting to Hawkeye API"
                return_response["status"] = 500
                self.__log_result(return_response)
                return return_response
            if response.status in range(200, 300):
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status

            if response.status == 401:
                await self.login()
                return_response["body"] = "Got 401 from Hawkeye"
                return_response["status"] = response.status
                self.__log_result(return_response)
                if retries >= self._config.HAWKEYE_CONFIG["retries"]:
                    self._logger.error(f"Maximum number of retries exceeded")
                    return return_response
                retries += 1
                return_response = await _get_test_result_details()

            if response.status in range(500, 513):
                return_response["body"] = "Got internal error from Hawkeye"
                return_response["status"] = 500
                self.__log_result(return_response)
            return return_response

        retries = 0
        return await _get_test_result_details()

    def __log_result(self, result: dict):
        body, status = result["body"], result["status"]

        if status == 400:
            self._logger.error(f"Got error from Hawkeye -> {body}")
        if status == 401:
            self._logger.error(f"Authentication error -> {body}")
        if status in range(500, 513):
            self._logger.error(f"Got {status} from Hawkeye")
