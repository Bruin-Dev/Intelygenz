from collections import defaultdict

import asyncio
import requests
from tenacity import retry, wait_exponential, stop_after_delay


class VelocloudClient:

    def __init__(self, config, logger):
        self._config = config.VELOCLOUD_CONFIG
        self._clients = list()
        self._logger = logger

    def instantiate_and_connect_clients(self):
        self._clients = [
            self._create_and_connect_client(cred_block['url'], cred_block['username'], cred_block['password']) for
            cred_block in self._config['servers']]

    def _create_and_connect_client(self, host, user, password):
        self._logger.info(f'Logging in host: {host} to velocloud')

        client = dict()
        client['host'] = host
        headers = self._create_headers_by_host(host, user, password)
        if headers["status"] in range(200, 300):
            self._logger.info("Connection successful")
            client['headers'] = headers["body"]
            return client
        else:
            self._logger.info(f'Connection wasn\'t possible, error {headers["status"]}')
            self._logger.info(headers['body'])
            return

    def _create_headers_by_host(self, host, user, password):
        @retry(wait=wait_exponential(multiplier=self._config['multiplier'],
                                     min=self._config['min']),
               stop=stop_after_delay(self._config['stop_delay']), reraise=True)
        def _create_headers_by_host():
            credentials = {
                "username": user,
                "password": password
            }
            post = {
                'headers': {"Content-Type": "application/json"},
                'json': credentials,
                'allow_redirects': False,
                'verify': self._config['verify_ssl']
            }
            uri = f"https://{host}/portal/rest/login/operatorLogin"
            response = requests.post(uri, **post)
            return_response = dict.fromkeys(["body", "status"])

            if response.status_code in range(200, 300):
                self._logger.info(f'Host: {host} logged in')
                session_index = response.headers['Set-Cookie'].find("velocloud.session")
                session_end = response.headers['Set-Cookie'].find(";", session_index)

                cookie = response.headers['Set-Cookie'][session_index:session_end]

                headers = {
                    "Cookie": cookie,
                    "Content-Type": "application/json-patch+json",
                    "Cache-control": "no-cache, no-store, no-transform, max-age=0, only-if-cached",
                }
                return_response["body"] = headers
                return_response["status"] = response.status_code
            if response.status_code == 302:
                self._logger.error(f"Got 302 from Bruin, re-login with credentials and retrying get headers")
                return_response["body"] = f"Maximum retries while relogin"
                return_response["status"] = 302
                raise Exception(return_response)

            return return_response

        try:
            return _create_headers_by_host()
        except Exception as e:
            return e.args[0]

    def _get_header_by_host(self, host):
        host_client = [client
                       for client in self._clients
                       if host == client['host']][0]
        return host_client

    def get_edge_information(self, edge):
        @retry(wait=wait_exponential(multiplier=self._config['multiplier'], min=self._config['min']),
               stop=stop_after_delay(self._config['stop_delay']), reraise=True)
        def get_edge_information():
            target_host_client = self._get_header_by_host(edge["host"])
            edgeids = {"enterpriseId": edge["enterprise_id"], "id": edge["edge_id"]}
            response = requests.post(f"https://{edge['host']}/portal/rest/edge/getEdge",
                                     json=edgeids,
                                     headers=target_host_client['headers'],
                                     verify=self._config['verify_ssl'])
            return_response = dict.fromkeys(["body", "status"])
            if response.status_code in range(200, 300):
                return_response["body"] = self._json_return(response.json())
                return_response["status"] = response.status_code
                return return_response
            if response.status_code == 400:
                return_response["body"] = response.json()
                return_response["status"] = response.status_code
                self._logger.error(f"Got error from Velocloud {response.json()}")
            if response.status_code in range(500, 513):
                self._logger.error(f"Got {response.status_code}. Retrying...")
                return_response["body"] = f"Got internal error from Velocloud"
                return_response["status"] = 500
                raise Exception(return_response)

            return return_response

        try:
            return get_edge_information()
        except Exception as e:
            return e.args[0]

    def get_link_information(self, edge, interval):
        @retry(wait=wait_exponential(multiplier=self._config['multiplier'], min=self._config['min']),
               stop=stop_after_delay(self._config['stop_delay']), reraise=True)
        def get_link_information():
            target_host_client = self._get_header_by_host(edge["host"])
            edgeids = {"enterpriseId": edge["enterprise_id"], "id": edge["edge_id"], "interval": interval}
            response = requests.post(f"https://{edge['host']}/portal/rest/metrics/getEdgeLinkMetrics",
                                     json=edgeids,
                                     headers=target_host_client['headers'],
                                     verify=self._config['verify_ssl'])

            return_response = dict.fromkeys(["body", "status"])
            if response.status_code in range(200, 300):
                return_response["body"] = self._json_return(response.json())
                return_response["status"] = response.status_code
                return return_response
            if response.status_code == 400:
                return_response["body"] = response.json()
                return_response["status"] = response.status_code
                self._logger.error(f"Got error from Velocloud {response.json()}")
            if response.status_code in range(500, 513):
                self._logger.error(f"Got {response.status_code}. Retrying...")
                return_response["body"] = f"Got internal error from Velocloud"
                return_response["status"] = 500
                raise Exception(return_response)

            return return_response

        try:
            return get_link_information()
        except Exception as e:
            return e.args[0]

    def get_link_service_groups_information(self, edge, interval):
        @retry(wait=wait_exponential(multiplier=self._config['multiplier'], min=self._config['min']),
               stop=stop_after_delay(self._config['stop_delay']), reraise=True)
        def get_link_service_groups_information():
            target_host_client = self._get_header_by_host(edge["host"])
            edgeids = {"enterpriseId": edge["enterprise_id"], "id": edge["edge_id"], "interval": interval}
            response = requests.post(f"https://{edge['host']}/portal/rest/metrics/getEdgeAppLinkMetrics",
                                     json=edgeids,
                                     headers=target_host_client['headers'],
                                     verify=self._config['verify_ssl'])

            return_response = dict.fromkeys(["body", "status"])
            if response.status_code in range(200, 300):
                return_response["body"] = self._json_return(response.json())
                return_response["status"] = response.status_code
                return return_response
            if response.status_code == 400:
                return_response["body"] = response.json()
                return_response["status"] = response.status_code
                self._logger.error(f"Got error from Velocloud {response.json()}")
            if response.status_code in range(500, 513):
                self._logger.error(f"Got {response.status_code}. Retrying...")
                return_response["body"] = f"Got internal error from Velocloud"
                return_response["status"] = 500
                raise Exception(return_response)

            return return_response

        try:
            return get_link_service_groups_information()
        except Exception as e:
            return e.args[0]

    def get_enterprise_information(self, edge):
        @retry(wait=wait_exponential(multiplier=self._config['multiplier'], min=self._config['min']),
               stop=stop_after_delay(self._config['stop_delay']), reraise=True)
        def get_enterprise_information():
            target_host_client = self._get_header_by_host(edge["host"])
            body = {"enterpriseId": edge["enterprise_id"]}
            response = requests.post(f"https://{edge['host']}/portal/rest/enterprise/getEnterprise",
                                     json=body,
                                     headers=target_host_client['headers'],
                                     verify=self._config['verify_ssl'])

            return_response = dict.fromkeys(["body", "status"])
            if response.status_code in range(200, 300):
                return_response["body"] = self._json_return(response.json())
                return_response["status"] = response.status_code
                return return_response
            if response.status_code == 400:
                return_response["body"] = response.json()
                return_response["status"] = response.status_code
                self._logger.error(f"Got error from Velocloud {response.json()}")
            if response.status_code in range(500, 513):
                self._logger.error(f"Got {response.status_code}. Retrying...")
                return_response["body"] = f"Got internal error from Velocloud"
                return_response["status"] = 500
                raise Exception(return_response)

            return return_response

        try:
            return get_enterprise_information()
        except Exception as e:
            return e.args[0]

    def get_all_edge_events(self, edge, start, end, limit):
        @retry(wait=wait_exponential(multiplier=self._config['multiplier'], min=self._config['min']),
               stop=stop_after_delay(self._config['stop_delay']), reraise=True)
        def get_all_edge_events():
            target_host_client = self._get_header_by_host(edge["host"])
            body = {"enterpriseId": edge["enterprise_id"],
                    "interval": {"start": start, "end": end},
                    "filter": {"limit": limit},
                    "edgeId": [edge["edge_id"]]}

            response = requests.post(f"https://{edge['host']}/portal/rest/event/getEnterpriseEvents",
                                     json=body,
                                     headers=target_host_client['headers'],
                                     verify=False)

            return_response = dict.fromkeys(["body", "status"])
            if response.status_code in range(200, 300):
                return_response["body"] = self._json_return(response.json())
                return_response["status"] = response.status_code
                return return_response
            if response.status_code == 400:
                return_response["body"] = response.json()
                return_response["status"] = response.status_code
                self._logger.error(f"Got error from Velocloud {response.json()}")
            if response.status_code in range(500, 513):
                self._logger.error(f"Got {response.status_code}. Retrying...")
                return_response["body"] = f"Got internal error from Velocloud"
                return_response["status"] = 500
                raise Exception(return_response)

            return return_response

        try:
            return get_all_edge_events()
        except Exception as e:
            return e.args[0]

    def get_all_enterprises_edges_with_host(self, filter):
        edges_by_enterprise_and_host = list()
        clients = self._clients

        if len(filter) > 0:
            clients = []
            for host in filter.keys():
                target_host_client = self._get_header_by_host(host)
                clients.append(target_host_client)
        else:
            filter = defaultdict(dict)

        response = {"body": None, "status": 200}
        for client in clients:
            res = self.get_monitoring_aggregates(client)
            if res["status"] not in range(200, 300):
                self._logger.error(f"Function [get_all_enterprises_edges_with_host] Error: \n"
                                   f"Status : {res['status']}, \n"
                                   f"Error Message: {res['body']}")
                response["body"] = res["body"]
                response["status"] = 500
                return response
            for enterprise in res["body"]["enterprises"]:
                if not enterprise["id"] in filter[client['host']] and len(filter[client['host']]) != 0:
                    continue

                edges_by_enterprise = self.get_all_enterprises_edges_by_id(client, enterprise["id"])
                if edges_by_enterprise["status"] not in range(200, 300):
                    response["body"] = res["body"]
                    response["status"] = 500
                    return response
                for edge in edges_by_enterprise["body"]:
                    edges_by_enterprise_and_host.append(
                        {"host": client["host"],
                         "enterprise_id": enterprise["id"],
                         "edge_id": edge["id"]})
        response['body'] = edges_by_enterprise_and_host
        return response

    async def get_all_enterprises_edges_with_host_by_serial(self):
        serial_to_edge_id = defaultdict(list)
        loop = asyncio.get_event_loop()
        for client in self._clients:
            res = self.get_monitoring_aggregates(client)
            if res["status"] not in range(200, 300):
                self._logger.error(f"Function [get_all_enterprises_edges_with_host_by_serial] Error: \n"
                                   f"Status : {res['status']}, \n"
                                   f"Error Message: {res['body']}")
                continue

            futures = [
                loop.run_in_executor(
                    None,
                    self.get_all_enterprises_edges_by_id,
                    client,
                    enterprise["id"]
                )
                for enterprise in res["body"]["enterprises"]
            ]
            for enterprise_info in await asyncio.gather(*futures):
                for edge in enterprise_info["body"]:
                    # serialNumber is the serial number of the current edge
                    # haSerialNumber is the serial number of the backup edge of the current edge
                    if edge["haSerialNumber"] is not None:
                        serial_to_edge_id[edge["haSerialNumber"]].append({"host": client["host"],
                                                                          "enterprise_id": edge["enterpriseId"],
                                                                          "edge_id": edge["id"]})
                    serial_to_edge_id[edge["serialNumber"]].append({"host": client["host"],
                                                                    "enterprise_id": edge["enterpriseId"],
                                                                    "edge_id": edge["id"]})

        return serial_to_edge_id

    def get_all_hosts_edge_count(self):
        sum = 0
        for client in self._clients:
            res = self.get_monitoring_aggregates(client)
            if res["status"] in range(200, 300):
                sum += res["body"]["edgeCount"]
            else:
                self._logger.error(f"Function [get_all_hosts_edge_count] Error:\n Status: {res['status']},\n "
                                   f"Error Message: {res['body']}")

        return sum

    def get_monitoring_aggregates(self, client):
        @retry(wait=wait_exponential(multiplier=self._config['multiplier'], min=self._config['min']),
               stop=stop_after_delay(self._config['stop_delay']), reraise=True)
        def get_monitoring_aggregates():
            response = requests.post(f"https://{client['host']}/portal/rest/monitoring/getAggregates",
                                     json={},
                                     headers=client['headers'],
                                     verify=False)

            return_response = dict.fromkeys(["body", "status"])
            if response.status_code in range(200, 300):
                return_response["body"] = self._json_return(response.json())
                return_response["status"] = response.status_code
                return return_response
            if response.status_code == 400:
                return_response["body"] = response.json()
                return_response["status"] = response.status_code
                self._logger.error(f"Got error from Velocloud {response.json()}")
            if response.status_code in range(500, 513):
                self._logger.error(f"Got {response.status_code}. Retrying...")
                return_response["body"] = f"Got internal error from Velocloud"
                return_response["status"] = 500
                raise Exception(return_response)

            return return_response

        try:
            return get_monitoring_aggregates()
        except Exception as e:
            return e.args[0]

    def get_all_enterprises_edges_by_id(self, client, enterprise_id):
        @retry(wait=wait_exponential(multiplier=self._config['multiplier'], min=self._config['min']),
               stop=stop_after_delay(self._config['stop_delay']), reraise=True)
        def get_all_enterprises_edges_by_id():
            body = {"enterpriseId": enterprise_id}
            response = requests.post(f"https://{client['host']}/portal/rest/enterprise/getEnterpriseEdges",
                                     json=body,
                                     headers=client['headers'],
                                     verify=False)
            return_response = dict.fromkeys(["body", "status"])
            if response.status_code in range(200, 300):
                return_response["body"] = self._json_return(response.json())
                return_response["status"] = response.status_code
                return return_response
            if response.status_code == 400:
                return_response["body"] = response.json()
                return_response["status"] = response.status_code
                self._logger.error(f"Got error from Velocloud {response.json()}")
            if response.status_code in range(500, 513):
                self._logger.error(f"Got {response.status_code}. Retrying...")
                return_response["body"] = f"Got internal error from Velocloud"
                return_response["status"] = 500
                raise Exception(return_response)

            return return_response

        try:
            return get_all_enterprises_edges_by_id()
        except Exception as e:
            return e.args[0]

    def get_all_enterprise_names(self):
        enterprise_names = list()
        response = {"body": None, "status": 200}
        for client in self._clients:
            res = self.get_monitoring_aggregates(client)
            if res["status"] not in range(200, 300):
                self._logger.error(f"Function [get_all_enterprise_names] Error: \n"
                                   f"Status : {res['status']}, \n"
                                   f"Error Message: {res['body']}")
                response["body"] = res["body"]
                response["status"] = 500
                continue
            for enterprise in res["body"]["enterprises"]:
                enterprise_names.append({
                    "enterprise_name": enterprise["name"]
                })
        response['body'] = enterprise_names
        return response

    def _json_return(self, response):
        if isinstance(response, dict):
            if 'error' in response.keys():
                if 'tokenError' in response['error']['message']:
                    self._logger.info(f'Response returned: {response}. Attempting to relogin')
                    self.instantiate_and_connect_clients()
                    raise Exception
                else:
                    self._logger.error(f'Error response returned: {response}')
        return response
