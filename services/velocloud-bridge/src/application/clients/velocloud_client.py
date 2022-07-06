import asyncio
from datetime import datetime
from typing import Any, Dict, List

import aiohttp
from apscheduler.jobstores.base import ConflictingIdError
from pytz import timezone


class VelocloudClient:
    def __init__(self, config, logger, scheduler):
        self._config = config
        self._clients = list()
        self._logger = logger
        self._scheduler = scheduler
        self._session = aiohttp.ClientSession()

    def __del__(self):
        asyncio.get_event_loop().run_until_complete(self._session.close())

    async def instantiate_and_connect_clients(self):
        self._clients = [
            await self._create_and_connect_client(cred_block["url"], cred_block["username"], cred_block["password"])
            for cred_block in self._config.VELOCLOUD_CONFIG["servers"]
        ]

    async def _start_relogin_job(self, host):
        self._logger.info(f"Scheduling relogin job for host {host}...")

        tz = timezone(self._config.TIMEZONE)
        run_date = datetime.now(tz)

        try:
            params = {
                "host": host,
            }
            self._scheduler.add_job(
                self._relogin_client,
                "date",
                run_date=run_date,
                replace_existing=False,
                misfire_grace_time=9999,
                id=f"_relogin_client{host}",
                kwargs=params,
            )
            self._logger.info(f"Relogin job for host {host} has been scheduled")

        except ConflictingIdError as conflict:
            self._logger.info(f"Skipping start of relogin job for host {host}. Reason: {conflict}")

    def _get_cred_block(self, host):
        for cred_block in self._config.VELOCLOUD_CONFIG["servers"]:
            if host == cred_block["url"]:
                return cred_block

    async def _relogin_client(self, host):
        self._logger.info(f"Relogging in host: {host} to velocloud")

        creds = self._get_cred_block(host)

        for client in self._clients:
            if host == client["host"]:
                client["headers"] = {}
                connected_client = await self._create_and_connect_client(host, creds["username"], creds["password"])
                client["headers"] = connected_client["headers"]
                break

    async def _create_and_connect_client(self, host, user, password):
        self._logger.info(f"Logging in host: {host} to velocloud")

        client = dict()
        client["host"] = host
        headers = await self._create_headers_by_host(host, user, password)
        if headers["status"] in range(200, 300):
            self._logger.info("Connection successful")
            client["headers"] = headers["body"]
        else:
            self._logger.info(f"Connection wasn't possible, error {headers['status']}")
            self._logger.info(headers["body"])
            client["headers"] = {}
        return client

    async def _create_headers_by_host(self, host, user, password):
        try:
            post = {
                "headers": {"Content-Type": "application/json"},
                "json": {"username": user, "password": password},
                "allow_redirects": False,
                "ssl": self._config.VELOCLOUD_CONFIG["verify_ssl"],
            }
            response = await self._session.post(f"https://{host}/portal/rest/login/operatorLogin", **post)
            return_response = dict.fromkeys(["body", "status"])
            if response.status in range(200, 300):
                self._logger.info(f"Host: {host} logged in")
                session_index = response.headers["Set-Cookie"].find("velocloud.session")
                session_end = response.headers["Set-Cookie"].find(";", session_index)

                headers = {
                    "Cookie": response.headers["Set-Cookie"][session_index:session_end],
                    "Content-Type": "application/json-patch+json",
                    "Cache-control": "no-cache, no-store, no-transform, max-age=0, only-if-cached",
                }
                return_response["body"] = headers
                return_response["status"] = response.status
            if response.status == 302:
                self._logger.error(f"Got 302 from velocloud")
                return_response["body"] = f"Got an error trying to login"
                return_response["status"] = 302

            return return_response
        except Exception as e:
            return {"body": e.args[0], "status": 500}

    def _get_header_by_host(self, host):
        host_client = [client for client in self._clients if host == client["host"]]
        if len(host_client) > 0:
            self._logger.info(f"Found host: {host} in client array")
            return host_client[0]
        self._logger.info(f"Host: {host} not found in client array")
        return None

    async def get_all_events(self, host, body):
        try:
            return_response = dict.fromkeys(["body", "status"])
            target_host_client = self._get_header_by_host(host)

            if target_host_client is None:
                self._logger.error(f"Cannot find a client to connect to {host}")
                return_response["body"] = f"Cannot find a client to connect to {host}"
                return_response["status"] = 404
                await self._start_relogin_job(host)
                return return_response

            response = await self._session.post(
                f"https://{host}/portal/rest/event/getEnterpriseEvents",
                json=body,
                headers=target_host_client["headers"],
                ssl=self._config.VELOCLOUD_CONFIG["verify_ssl"],
            )

            if response.status in range(200, 300):
                response_json = await response.json()
                return_response["body"] = await self._json_return(response_json, host)
                return_response["status"] = response.status
                return return_response
            if response.status == 400:
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status
                self._logger.error(f"Got error from Velocloud {response_json}")
            if response.status in range(500, 513):
                self._logger.error(f"Got {response.status}")
                return_response["body"] = f"Got internal error from Velocloud"
                return_response["status"] = 500

            return return_response
        except Exception as e:
            return {"body": e.args[0], "status": 500}

    async def get_monitoring_aggregates(self, client):
        try:
            response = await self._session.post(
                f"https://{client['host']}/portal/rest/monitoring/getAggregates",
                json={},
                headers=client["headers"],
                ssl=self._config.VELOCLOUD_CONFIG["verify_ssl"],
            )

            return_response = dict.fromkeys(["body", "status"])
            if response.status in range(200, 300):
                response_json = await response.json()
                return_response["body"] = await self._json_return(response_json, client["host"])
                return_response["status"] = response.status
                return return_response
            if response.status == 400:
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status
                self._logger.error(f"Got error from Velocloud {response_json}")
            if response.status in range(500, 513):
                self._logger.error(f"Got {response.status}")
                return_response["body"] = f"Got internal error from Velocloud"
                return_response["status"] = 500

            return return_response
        except Exception as e:
            return {"body": e.args[0], "status": 500}

    async def get_all_enterprise_names(self):
        enterprise_names = list()
        response = {"body": None, "status": 200}
        for client in self._clients:
            res = await self.get_monitoring_aggregates(client)
            if res["status"] not in range(200, 300):
                self._logger.error(
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

    async def _json_return(self, response, host):
        if isinstance(response, dict):
            if "error" in response.keys():
                if "tokenError" in response["error"]["message"]:
                    self._logger.info(f"Response returned: {response}. Attempting to relogin")
                    await self._start_relogin_job(host)
                else:
                    self._logger.error(f"Error response returned: {response}")
        return response

    async def get_links_with_edge_info(self, velocloud_host: str):
        result = dict.fromkeys(["body", "status"])

        request_body = {}
        target_host_client = self._get_header_by_host(velocloud_host)

        if target_host_client is None:
            await self._start_relogin_job(velocloud_host)

            result["body"] = f"Cannot find a client to connect to host {velocloud_host}"
            result["status"] = 404
            self.__log_result(result)

            return result

        try:
            self._logger.info(f'Getting links with edge info from Velocloud host "{velocloud_host}"...')

            response = await self._session.post(
                f"https://{velocloud_host}/portal/rest/monitoring/getEnterpriseEdgeLinkStatus",
                json=request_body,
                headers=target_host_client["headers"],
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

        await self.__schedule_relogin_job_if_needed(velocloud_host, response)

        self._logger.info(
            f"Got HTTP {response.status} from Velocloud after claiming links with edge info for host {velocloud_host}"
        )

        result["body"] = await response.json()
        result["status"] = response.status

        self.__log_result(result)

        return result

    async def get_links_metric_info(self, velocloud_host: str, interval: dict):
        result = dict.fromkeys(["body", "status"])

        request_body = {
            "interval": interval,
        }
        target_host_client = self._get_header_by_host(velocloud_host)

        if target_host_client is None:
            await self._start_relogin_job(velocloud_host)

            result["body"] = f"Cannot find a client to connect to host {velocloud_host}"
            result["status"] = 404
            self.__log_result(result)

            return result

        try:
            self._logger.info(f'Getting links metric info from Velocloud host "{velocloud_host}"...')

            response = await self._session.post(
                f"https://{velocloud_host}/portal/rest/monitoring/getAggregateEdgeLinkMetrics",
                json=request_body,
                headers=target_host_client["headers"],
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

        await self.__schedule_relogin_job_if_needed(velocloud_host, response)

        self._logger.info(
            f"Got HTTP {response.status} from Velocloud after claiming links metric info for host {velocloud_host}"
        )

        result["body"] = await response.json()
        result["status"] = response.status

        self.__log_result(result)

        return result

    async def get_edge_links_series(self, velocloud_host: str, payload):
        target_host_client = self._get_header_by_host(velocloud_host)
        result = dict.fromkeys(["body", "status"])
        self._logger.info(
            f"Trying to get edge links series for payload {payload} and" f' from Velocloud host "{velocloud_host}"...'
        )
        if target_host_client is None:
            await self._start_relogin_job(velocloud_host)

            result["body"] = f"Cannot find a client to connect to host {velocloud_host}"
            result["status"] = 404
            self.__log_result(result)

            return result

        try:
            response = await self._session.post(
                f"https://{velocloud_host}/portal/rest/metrics/getEdgeLinkSeries",
                json=payload,
                headers=target_host_client["headers"],
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

        await self.__schedule_relogin_job_if_needed(velocloud_host, response)

        self._logger.info(
            f"Got HTTP {response.status} from Velocloud after edge link series for {payload}"
            f"and host {velocloud_host}"
        )

        result["body"] = await response.json()
        result["status"] = response.status

        self.__log_result(result)

        return result

    async def get_enterprise_edges(self, velocloud_host: str, enterprise_id: str):
        result = dict.fromkeys(["body", "status"])

        request_body = {"enterpriseId": enterprise_id, "with": ["links"]}
        target_host_client = self._get_header_by_host(velocloud_host)

        if target_host_client is None:
            await self._start_relogin_job(velocloud_host)

            result["body"] = f"Cannot find a client to connect to host {velocloud_host}"
            result["status"] = 404
            self.__log_result(result)

            return result

        try:
            self._logger.info(
                f"Getting all enterprise edges from enterprise ID {enterprise_id} and"
                f' from Velocloud host "{velocloud_host}"...'
            )

            response = await self._session.post(
                f"https://{velocloud_host}/portal/rest/enterprise/getEnterpriseEdges",
                json=request_body,
                headers=target_host_client["headers"],
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

        await self.__schedule_relogin_job_if_needed(velocloud_host, response)

        self._logger.info(
            f"Got HTTP {response.status} from Velocloud after getting enterpise edges for enterprise {enterprise_id}"
            f"and host {velocloud_host}"
        )

        result["body"] = await response.json()
        result["status"] = response.status

        self.__log_result(result)

        return result

    async def get_edge_configuration_modules(self, edge):
        velocloud_host = edge["host"]

        result = dict.fromkeys(["body", "status"])

        request_body = {
            "enterpriseId": edge["enterprise_id"],
            "edgeId": edge["edge_id"],
            "modules": [
                "WAN",
            ],
        }
        target_host_client = self._get_header_by_host(velocloud_host)

        if target_host_client is None:
            await self._start_relogin_job(velocloud_host)
            result["body"] = f"Cannot find a client to connect to host {velocloud_host}"
            result["status"] = 404
            self.__log_result(result)
            return result

        try:
            self._logger.info(f"Getting edge configuration modules for edge {edge}...")

            response = await self._session.post(
                f"https://{velocloud_host}/portal/rest/edge/getEdgeConfigurationModules",
                json=request_body,
                headers=target_host_client["headers"],
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

        await self.__schedule_relogin_job_if_needed(velocloud_host, response)

        self._logger.info(
            f"Got HTTP {response.status} from Velocloud after claiming edge configuration modules for edge {edge}"
        )
        result["body"] = await response.json()
        result["status"] = response.status

        self.__log_result(result)

        return result

    async def get_network_enterprises(self, velocloud_host: str, enterprise_ids: List[int]) -> Dict[str, Any]:
        result = dict.fromkeys(["body", "status"])
        request_body = {"enterprises": enterprise_ids, "with": ["edges"]}

        target_host_client = self._get_header_by_host(velocloud_host)
        try:
            self._logger.info(f"Getting network enterprise ids for {enterprise_ids}...")

            response = await self._session.post(
                f"https://{velocloud_host}/portal/rest/network/getNetworkEnterprises",
                json=request_body,
                headers=target_host_client["headers"],
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
                await self.__schedule_relogin_job_if_needed(velocloud_host, response)
                self._logger.info(
                    f"Got HTTP {response.status} from Velocloud after getting enterprise ids: {enterprise_ids}"
                )
                result["body"] = await response.json()
                result["status"] = response.status

        self.__log_result(result)

        return result

    async def get_network_gateways(self, velocloud_host: str):
        request_body = {}
        result = dict.fromkeys(["body", "status"])

        target_host_client = self._get_header_by_host(velocloud_host)

        if target_host_client is None:
            await self._start_relogin_job(velocloud_host)
            result["body"] = f"Cannot find a client to connect to host {velocloud_host}"
            result["status"] = 404
            self.__log_result(result)
            return result

        try:
            self._logger.info(f"Getting network gateways for host {velocloud_host}...")

            response = await self._session.post(
                url=f"https://{velocloud_host}/portal/rest/network/getNetworkGateways",
                json=request_body,
                headers=target_host_client["headers"],
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
            return result

        await self.__schedule_relogin_job_if_needed(velocloud_host, response)

        self._logger.info(
            f"Got HTTP {response.status} from Velocloud after getting network gateways for host {velocloud_host}"
        )

        result["body"] = await response.json()
        result["status"] = response.status

        self.__log_result(result)

        return result

    async def get_network_gateway_status(self, velocloud_host: str, since: str, metrics: List[str]):
        request_body = {"time": since, "metrics": metrics}
        result = dict.fromkeys(["body", "status"])

        target_host_client = self._get_header_by_host(velocloud_host)

        if target_host_client is None:
            await self._start_relogin_job(velocloud_host)
            result["body"] = f"Cannot find a client to connect to host {velocloud_host}"
            result["status"] = 404
            self.__log_result(result)
            return result

        try:
            self._logger.info(f"Getting network gateway status for host {velocloud_host}...")

            response = await self._session.post(
                url=f"https://{velocloud_host}/portal/rest/monitoring/getNetworkGatewayStatus",
                json=request_body,
                headers=target_host_client["headers"],
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
            return result

        await self.__schedule_relogin_job_if_needed(velocloud_host, response)

        self._logger.info(
            f"Got HTTP {response.status} from Velocloud after getting network gateway status "
            f"for host {velocloud_host}"
        )

        result["body"] = await response.json()
        result["status"] = response.status

        self.__log_result(result)

        return result

    async def __schedule_relogin_job_if_needed(self, velocloud_host: str, response: aiohttp.client.ClientResponse):
        if self.__token_expired(response):
            self._logger.info(f"Auth token expired for host {velocloud_host}. Scheduling re-login job...")
            await self._start_relogin_job(velocloud_host)

            response._body = f"Auth token expired for host {velocloud_host}"
            response.status = 401

    @staticmethod
    def __token_expired(response: aiohttp.client.ClientResponse) -> bool:
        return response.headers.get("Expires") == "0"

    def __log_result(self, result: dict):
        body, status = result["body"], result["status"]
        if status == 400:
            self._logger.error(f"Got error from Velocloud -> {body}")
        if status == 401:
            self._logger.error(f"Authentication error -> {body}")
        if status in range(500, 513):
            self._logger.error(f"Got {status} from Velocloud")
