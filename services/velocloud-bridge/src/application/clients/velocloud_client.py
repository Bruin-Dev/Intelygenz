import asyncio
import logging
from datetime import datetime
from typing import Any, List

import aiohttp
from apscheduler.jobstores.base import ConflictingIdError
from pytz import timezone

logger = logging.getLogger(__name__)


class VelocloudClient:
    def __init__(self, config, scheduler):
        self._config = config
        self._scheduler = scheduler

    async def create_session(self):
        self._session = aiohttp.ClientSession()

    def __del__(self):
        asyncio.get_event_loop().run_until_complete(self._session.close())

    async def _connect_to_all_hosts(self):
        logger.info(f"Connecting to all hosts...")

        for host in self._config.VELOCLOUD_CONFIG["credentials"]:
            await self._login(host)

    async def schedule_connect_to_all_hosts(self):
        logger.info(f"Scheduling job to connect to all hosts...")

        tz = timezone(self._config.TIMEZONE)
        next_run_time = datetime.now(tz)

        try:
            self._scheduler.add_job(
                self._connect_to_all_hosts,
                "interval",
                seconds=self._config.VELOCLOUD_CONFIG["login_interval"],
                next_run_time=next_run_time,
                replace_existing=False,
                id="_connect_to_all_hosts",
            )
            logger.info(f"Job to connect to all hosts has been scheduled")
        except ConflictingIdError as conflict:
            logger.error(f"Skipping start of job to connect to all hosts. Reason: {conflict}")

    def _get_headers(self):
        return {
            "Content-Type": "application/json-patch+json",
            "Cache-control": "no-cache, no-store, no-transform, max-age=0, only-if-cached",
        }

    async def _json_return(self, response, host):
        if isinstance(response, dict):
            if "error" in response.keys():
                if "tokenError" in response["error"]["message"]:
                    logger.info(f"Response returned: {response}. Logging in...")
                    await self._login(host)
                else:
                    logger.error(f"Error response returned: {response}")
        return response

    async def _login(self, host):
        try:
            logger.info(f"Logging in to host {host}...")

            response = await self._session.post(
                f"https://{host}/portal/rest/login/operatorLogin",
                headers={"Content-Type": "application/json"},
                json=self._config.VELOCLOUD_CONFIG["credentials"][host],
                ssl=self._config.VELOCLOUD_CONFIG["verify_ssl"],
                allow_redirects=False,
            )

            if response.status in range(200, 300):
                logger.info(f"Logged in to host {host} successfully")
            else:
                logger.error(f"Got HTTP {response.status} while logging in to host {host}")
        except Exception as e:
            logger.exception(e)

    async def get_all_events(self, host, body):
        await self.__login_if_missing_cookie(host)

        try:
            return_response = dict.fromkeys(["body", "status"])
            headers = self._get_headers()

            logger.info(f"Getting all events from host {host} using payload {body}...")
            response = await self._session.post(
                f"https://{host}/portal/rest/event/getEnterpriseEvents",
                json=body,
                headers=headers,
                ssl=self._config.VELOCLOUD_CONFIG["verify_ssl"],
            )

            if response.status in range(200, 300):
                logger.info(f"Got HTTP 200 from POST /event/getEnterpriseEvents for host {host} and payload {body}")
                response_json = await response.json()
                return_response["body"] = await self._json_return(response_json, host)
                return_response["status"] = response.status
                return return_response

            if response.status == 400:
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status
                logger.error(f"Got HTTP 400 from Velocloud: {response_json}")

            if response.status in range(500, 513):
                logger.error(f"Got HTTP {response.status} from Velocloud")
                return_response["body"] = f"Got internal error from Velocloud"
                return_response["status"] = 500

            await self.__login_if_needed(host, response)

            return return_response
        except Exception as e:
            logger.exception(e)
            return {
                "body": f"Exception thrown when getting all events from host {host} using payload {body}...",
                "status": 500
            }

    async def get_monitoring_aggregates(self, host):
        await self.__login_if_missing_cookie(host)

        try:
            logger.info(f"Getting monitoring aggregates for host {host}")
            headers = self._get_headers()
            response = await self._session.post(
                f"https://{host}/portal/rest/monitoring/getAggregates",
                json={},
                headers=headers,
                ssl=self._config.VELOCLOUD_CONFIG["verify_ssl"],
            )

            return_response = dict.fromkeys(["body", "status"])
            if response.status in range(200, 300):
                logger.info(f"Got HTTP 200 from POST /monitoring/getAggregates for host {host}")
                response_json = await response.json()
                return_response["body"] = await self._json_return(response_json, host)
                return_response["status"] = response.status
                return return_response
            if response.status == 400:
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status
                logger.error(f"Got HTTP 400 from Velocloud {response_json}")
            if response.status in range(500, 513):
                logger.error(f"Got HTTP {response.status}")
                return_response["body"] = f"Got internal error from Velocloud"
                return_response["status"] = 500

            return return_response
        except Exception as e:
            return {"body": e.args[0], "status": 500}

    async def get_all_enterprise_names(self):
        enterprise_names = list()
        response = {"body": None, "status": 200}
        for host in self._config.VELOCLOUD_CONFIG["credentials"]:
            res = await self.get_monitoring_aggregates(host)
            if res["status"] not in range(200, 300):
                logger.error(
                    f"Function [get_all_enterprise_names] Error: \n"
                    f"Status : {res['status']}, \n"
                    f"Error Message: {res['body']}"
                )
                response["body"] = res["body"]
                response["status"] = 500
                continue
            for enterprise in res["body"]["enterprises"]:
                enterprise_names.append({"enterprise_name": enterprise["name"]})
        response["body"] = enterprise_names
        return response

    async def get_links_with_edge_info(self, velocloud_host: str):
        await self.__login_if_missing_cookie(velocloud_host)

        result = dict.fromkeys(["body", "status"])

        request_body = {}
        headers = self._get_headers()

        try:
            logger.info(f'Getting links with edge info from Velocloud host "{velocloud_host}"...')

            response = await self._session.post(
                f"https://{velocloud_host}/portal/rest/monitoring/getEnterpriseEdgeLinkStatus",
                json=request_body,
                headers=headers,
                ssl=self._config.VELOCLOUD_CONFIG["verify_ssl"],
            )
        except aiohttp.ClientConnectionError:
            result["body"] = "Error while connecting to Velocloud API"
            result["status"] = 500
            self.__log_result(result)
            return result

        if response.status in range(500, 513):
            result["body"] = "Got internal error from Velocloud"
            result["status"] = 500
            self.__log_result(result)
            return result

        await self.__login_if_needed(velocloud_host, response)

        logger.info(
            f"Got HTTP {response.status} from Velocloud after claiming links with edge info for host {velocloud_host}"
        )

        result["body"] = await response.json()
        result["status"] = response.status

        self.__log_result(result)

        return result

    async def get_links_metric_info(self, velocloud_host: str, interval: dict):
        await self.__login_if_missing_cookie(velocloud_host)

        result = dict.fromkeys(["body", "status"])

        request_body = {
            "interval": interval,
        }
        headers = self._get_headers()

        try:
            logger.info(f'Getting links metric info from Velocloud host "{velocloud_host}" for interval {interval}...')

            response = await self._session.post(
                f"https://{velocloud_host}/portal/rest/monitoring/getAggregateEdgeLinkMetrics",
                json=request_body,
                headers=headers,
                ssl=self._config.VELOCLOUD_CONFIG["verify_ssl"],
            )
        except aiohttp.ClientConnectionError:
            result["body"] = "Error while connecting to Velocloud API"
            result["status"] = 500
            self.__log_result(result)
            return result

        if response.status in range(500, 513):
            result["body"] = "Got internal error from Velocloud"
            result["status"] = 500
            self.__log_result(result)
            return result

        await self.__login_if_needed(velocloud_host, response)

        logger.info(
            f"Got HTTP {response.status} from Velocloud after claiming links metric info for host {velocloud_host} and "
            f"interval {interval}"
        )

        result["body"] = await response.json()
        result["status"] = response.status

        self.__log_result(result)

        return result

    async def get_edge_links_series(self, velocloud_host: str, payload):
        await self.__login_if_missing_cookie(velocloud_host)

        headers = self._get_headers()
        result = dict.fromkeys(["body", "status"])
        logger.info(
            f"Trying to get edge links series for payload {payload} and from Velocloud host '{velocloud_host}'..."
        )

        logger.info(f'Trying to get edge links series for payload {payload} from Velocloud host "{velocloud_host}"...')
        try:
            response = await self._session.post(
                f"https://{velocloud_host}/portal/rest/metrics/getEdgeLinkSeries",
                json=payload,
                headers=headers,
                ssl=self._config.VELOCLOUD_CONFIG["verify_ssl"],
            )
        except aiohttp.ClientConnectionError:
            result["body"] = "Error while connecting to Velocloud API"
            result["status"] = 500
            self.__log_result(result)
            return result

        if response.status in range(500, 513):
            result["body"] = "Got internal error from Velocloud"
            result["status"] = 500
            self.__log_result(result)
            return result

        await self.__login_if_needed(velocloud_host, response)

        logger.info(
            f"Got HTTP {response.status} from Velocloud after fetching edge link series for {payload}"
            f"and host {velocloud_host}"
        )

        result["body"] = await response.json()
        result["status"] = response.status

        self.__log_result(result)

        return result

    async def get_enterprise_edges(self, velocloud_host: str, enterprise_id: str):
        await self.__login_if_missing_cookie(velocloud_host)

        result = dict.fromkeys(["body", "status"])

        request_body = {"enterpriseId": enterprise_id, "with": ["links"]}
        headers = self._get_headers()

        try:
            logger.info(
                f"Getting all enterprise edges from enterprise ID {enterprise_id} and"
                f' from Velocloud host "{velocloud_host}"...'
            )

            response = await self._session.post(
                f"https://{velocloud_host}/portal/rest/enterprise/getEnterpriseEdges",
                json=request_body,
                headers=headers,
                ssl=self._config.VELOCLOUD_CONFIG["verify_ssl"],
            )
        except aiohttp.ClientConnectionError:
            result["body"] = "Error while connecting to Velocloud API"
            result["status"] = 500
            self.__log_result(result)
            return result

        if response.status in range(500, 513):
            result["body"] = "Got internal error from Velocloud"
            result["status"] = 500
            self.__log_result(result)
            return result

        await self.__login_if_needed(velocloud_host, response)

        logger.info(
            f"Got HTTP {response.status} from Velocloud after getting enterprise edges for enterprise {enterprise_id}"
            f"and host {velocloud_host}"
        )

        result["body"] = await response.json()
        result["status"] = response.status

        self.__log_result(result)

        return result

    async def get_edge_configuration_modules(self, edge):
        velocloud_host = edge["host"]
        await self.__login_if_missing_cookie(velocloud_host)

        result = dict.fromkeys(["body", "status"])

        request_body = {
            "enterpriseId": edge["enterprise_id"],
            "edgeId": edge["edge_id"],
            "modules": [
                "WAN",
            ],
        }
        headers = self._get_headers()

        try:
            logger.info(f"Getting edge configuration modules for edge {edge}...")

            response = await self._session.post(
                f"https://{velocloud_host}/portal/rest/edge/getEdgeConfigurationModules",
                json=request_body,
                headers=headers,
                ssl=self._config.VELOCLOUD_CONFIG["verify_ssl"],
            )
        except aiohttp.ClientConnectionError:
            result["body"] = "Error while connecting to Velocloud API"
            result["status"] = 500
            self.__log_result(result)
            return result

        if response.status in range(500, 513):
            result["body"] = "Got internal error from Velocloud"
            result["status"] = 500
            self.__log_result(result)
            return result

        if response.status == 400:
            response = await response.json()
            result["body"] = f"Got 400 from Velocloud -> {response['error']['message']} for edge {edge}"
            result["status"] = 400
            return result

        await self.__login_if_needed(velocloud_host, response)

        logger.info(
            f"Got HTTP {response.status} from Velocloud after claiming edge configuration modules for edge {edge}"
        )
        result["body"] = await response.json()
        result["status"] = response.status

        self.__log_result(result)

        return result

    async def get_network_enterprises(self, velocloud_host: str, enterprise_ids: list[int]) -> dict[str, Any]:
        await self.__login_if_missing_cookie(velocloud_host)

        result = dict.fromkeys(["body", "status"])
        request_body = {"enterprises": enterprise_ids, "with": ["edges"]}

        headers = self._get_headers()
        try:
            logger.info(
                f"Getting network enterprise edges for host {velocloud_host} and enterprises {enterprise_ids}..."
            )

            response = await self._session.post(
                f"https://{velocloud_host}/portal/rest/network/getNetworkEnterprises",
                json=request_body,
                headers=headers,
                ssl=self._config.VELOCLOUD_CONFIG["verify_ssl"],
            )
        except aiohttp.ClientConnectionError:
            result["body"] = "Error while connecting to Velocloud API"
            result["status"] = 500
        else:
            status = response.status
            if status in range(500, 513):
                result["body"] = "Got internal error from Velocloud"
                result["status"] = 500
            elif status == 400:
                error = await response.json()
                message = error["error"]["message"]
                result["body"] = f"Got 400 from Velocloud --> {message} for enterprise ids: {enterprise_ids}"
                result["status"] = 400
            else:
                await self.__login_if_needed(velocloud_host, response)
                logger.info(
                    f"Got HTTP {response.status} from Velocloud after getting enterprise ids: {enterprise_ids} "
                    f"from host {velocloud_host}"
                )
                result["body"] = await response.json()
                result["status"] = response.status

        self.__log_result(result)

        return result

    async def get_network_gateways(self, velocloud_host: str):
        await self.__login_if_missing_cookie(velocloud_host)

        request_body = {}
        result = dict.fromkeys(["body", "status"])

        headers = self._get_headers()
        try:
            logger.info(f"Getting network gateways for host {velocloud_host}...")

            response = await self._session.post(
                url=f"https://{velocloud_host}/portal/rest/network/getNetworkGateways",
                json=request_body,
                headers=headers,
                ssl=self._config.VELOCLOUD_CONFIG["verify_ssl"],
            )
        except aiohttp.ClientConnectionError:
            result["body"] = "Error while connecting to Velocloud API"
            result["status"] = 500
            self.__log_result(result)
            return result

        if response.status in range(500, 513):
            result["body"] = "Got internal error from Velocloud"
            result["status"] = 500
            self.__log_result(result)
            return result

        if response.status == 400:
            response = await response.json()
            result["body"] = f"Got 400 from Velocloud -> {response['error']['message']} for host {velocloud_host}"
            result["status"] = 400
            self.__log_result(result)
            return result

        await self.__login_if_needed(velocloud_host, response)

        logger.info(
            f"Got HTTP {response.status} from Velocloud after getting network gateways for host {velocloud_host}"
        )

        result["body"] = await response.json()
        result["status"] = response.status

        self.__log_result(result)

        return result

    async def get_gateway_status_metrics(
        self, velocloud_host: str, gateway_id: int, interval: dict, metrics: List[str]
    ):
        await self.__login_if_missing_cookie(velocloud_host)

        request_body = {
            "gatewayId": gateway_id,
            "interval": interval,
            "metrics": metrics,
        }
        result = dict.fromkeys(["body", "status"])

        headers = self._get_headers()
        try:
            logger.info(
                f"Getting gateway status metrics for gateway {gateway_id} and host {velocloud_host} in "
                f"interval {interval}..."
            )

            response = await self._session.post(
                url=f"https://{velocloud_host}/portal/rest/metrics/getGatewayStatusMetrics",
                json=request_body,
                headers=headers,
                ssl=self._config.VELOCLOUD_CONFIG["verify_ssl"],
            )
        except aiohttp.ClientConnectionError:
            result["body"] = "Error while connecting to Velocloud API"
            result["status"] = 500
            self.__log_result(result)
            return result

        if response.status in range(500, 513):
            result["body"] = "Got internal error from Velocloud"
            result["status"] = 500
            self.__log_result(result)
            return result

        if response.status == 400:
            response = await response.json()
            result["body"] = (
                f"Got 400 from Velocloud -> {response['error']['message']} for gateway {gateway_id} "
                f"and host {velocloud_host}"
            )
            result["status"] = 400
            self.__log_result(result)
            return result

        await self.__login_if_needed(velocloud_host, response)

        logger.info(
            f"Got HTTP {response.status} from Velocloud after getting gateway status metrics for gateway {gateway_id} "
            f"and host {velocloud_host} in interval {interval}"
        )

        result["body"] = await response.json()
        result["status"] = response.status

        self.__log_result(result)

        return result

    async def __login_if_needed(self, velocloud_host: str, response: aiohttp.client.ClientResponse):
        if await self.__token_expired(response):
            logger.info(f"Auth token expired for host {velocloud_host}. Logging in...")
            await self._login(velocloud_host)
            response.status = 401

    async def __login_if_missing_cookie(self, velocloud_host: str):
        if 'velocloud.session' not in self._session.cookie_jar.filter_cookies(f"https://{velocloud_host}"):
            await self._login(velocloud_host)

    @staticmethod
    async def __token_expired(response: aiohttp.client.ClientResponse) -> bool:
        if response.headers.get("Expires") == "0":
            json_data = await response.json()
            return (
                isinstance(json_data, dict)
                and json_data.get("error", {}).get("message", None) == "tokenError [expired session cookie]"
            )

        return False

    def __log_result(self, result: dict):
        body, status = result["body"], result["status"]
        if status == 400:
            logger.error(f"Got error from Velocloud -> {body}")
        if status == 401:
            logger.error(f"Authentication error -> {body}")
        if status in range(500, 513):
            logger.error(f"Got {status} from Velocloud")
