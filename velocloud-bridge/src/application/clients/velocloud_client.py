import json

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
        client['headers'] = self._create_headers_by_host(host, user, password)

        return client

    def _create_headers_by_host(self, host, user, password):
        @retry(wait=wait_exponential(multiplier=self._config['multiplier'],
                                     min=self._config['min']),
               stop=stop_after_delay(self._config['stop_delay']))
        def _create_headers_by_host():
            credentials = {
                "username": user,
                "password": password
            }
            response = requests.post(f"https://{host}/portal/rest/login/operatorLogin",
                                     headers={"Content-Type": "application/json"},
                                     data=credentials,
                                     allow_redirects=False,
                                     verify=self._config['verify_ssl'])
            if response.status_code in range(200, 299):
                self._logger.info(f'Host: {host} logged in')
                session_index = response.headers['Set-Cookie'].find("velocloud.session")
                session_end = response.headers['Set-Cookie'].find(";", session_index)

                cookie = response.headers['Set-Cookie'][session_index:session_end]

                headers = {
                    "Cookie": cookie,
                    "Content-Type": "application/json-patch+json",
                    "Cache-control": "no-cache, no-store, no-transform, max-age=0, only-if-cached",
                }

                return headers
            else:
                raise Exception

        return _create_headers_by_host()

    def _get_header_by_host(self, host):
        host_client = [client
                       for client in self._clients
                       if host == client['host']][0]
        return host_client

    def get_edge_information(self, edge):

        @retry(wait=wait_exponential(multiplier=self._config['multiplier'],
                                     min=self._config['min']),
               stop=stop_after_delay(self._config['stop_delay']))
        def get_edge_information():
            target_host_client = self._get_header_by_host(edge["host"])
            edgeids = {"enterpriseId": edge["enterprise_id"], "id": edge["edge_id"]}
            response = requests.post(f"https://{edge['host']}/portal/rest/edge/getEdge",
                                     data=json.dumps(edgeids),
                                     headers=target_host_client['headers'],
                                     verify=self._config['verify_ssl'])

            return self._json_return(response.json())

        return get_edge_information()

    def get_link_information(self, edge, interval):

        @retry(wait=wait_exponential(multiplier=self._config['multiplier'],
                                     min=self._config['min']),
               stop=stop_after_delay(self._config['stop_delay']))
        def get_link_information():
            target_host_client = self._get_header_by_host(edge["host"])
            edgeids = {"enterpriseId": edge["enterprise_id"], "id": edge["edge_id"], "interval": interval}
            response = requests.post(f"https://{edge['host']}/portal/rest/metrics/getEdgeLinkMetrics",
                                     data=json.dumps(edgeids),
                                     headers=target_host_client['headers'],
                                     verify=self._config['verify_ssl'])

            return self._json_return(response.json())

        return get_link_information()

    def get_link_service_groups_information(self, edge, interval):

        @retry(wait=wait_exponential(multiplier=self._config['multiplier'],
                                     min=self._config['min']),
               stop=stop_after_delay(self._config['stop_delay']))
        def get_link_service_groups_information():
            target_host_client = self._get_header_by_host(edge["host"])
            edgeids = {"enterpriseId": edge["enterprise_id"], "id": edge["edge_id"], "interval": interval}
            response = requests.post(f"https://{edge['host']}/portal/rest/metrics/getEdgeAppLinkMetrics",
                                     data=json.dumps(edgeids),
                                     headers=target_host_client['headers'],
                                     verify=self._config['verify_ssl'])

            return self._json_return(response.json())

        return get_link_service_groups_information()

    def get_enterprise_information(self, edge):

        @retry(wait=wait_exponential(multiplier=self._config['multiplier'],
                                     min=self._config['min']),
               stop=stop_after_delay(self._config['stop_delay']))
        def get_enterprise_information():
            target_host_client = self._get_header_by_host(edge["host"])
            body = {"enterpriseId": edge["enterprise_id"]}
            response = requests.post(f"https://{edge['host']}/portal/rest/enterprise/getEnterprise",
                                     data=json.dumps(body),
                                     headers=target_host_client['headers'],
                                     verify=self._config['verify_ssl'])

            return self._json_return(response.json())

        return get_enterprise_information()

    def get_all_edge_events(self, edge, start, end, limit):

        @retry(wait=wait_exponential(multiplier=self._config['multiplier'],
                                     min=self._config['min']),
               stop=stop_after_delay(self._config['stop_delay']))
        def get_all_edge_events():
            target_host_client = self._get_header_by_host(edge["host"])
            body = {"enterpriseId": edge["enterprise_id"],
                    "interval": {"start": start, "end": end},
                    "filter": {"limit": limit},
                    "edgeId": [edge["edge_id"]]}

            response = requests.post(f"https://{edge['host']}/portal/rest/event/getEnterpriseEvents",
                                     data=json.dumps(body),
                                     headers=target_host_client['headers'],
                                     verify=False)

            return self._json_return(response.json())

        return get_all_edge_events()

    def get_all_enterprises_edges_with_host(self):
        edges_by_enterprise_and_host = list()
        for client in self._clients:
            res = self.get_monitoring_aggregates(client)
            for enterprise in res["enterprises"]:
                edges_by_enterprise = self.get_all_enterprises_edges_by_id(client, enterprise["id"])
                for edge in edges_by_enterprise:
                    edges_by_enterprise_and_host.append(
                        {"host": client["host"],
                         "enterprise_id": enterprise["id"],
                         "edge_id": edge["id"]})

        return edges_by_enterprise_and_host

    def get_all_hosts_edge_count(self):
        sum = 0
        for client in self._clients:
            res = self.get_monitoring_aggregates(client)
            sum += res["edgeCount"]

        return sum

    def get_monitoring_aggregates(self, client):

        @retry(wait=wait_exponential(multiplier=self._config['multiplier'],
                                     min=self._config['min']),
               stop=stop_after_delay(self._config['stop_delay']))
        def get_monitoring_aggregates():
            response = requests.post(f"https://{client['host']}/portal/rest/monitoring/getAggregates",
                                     data={},
                                     headers=client['headers'],
                                     verify=False)
            return self._json_return(response.json())

        return get_monitoring_aggregates()

    def get_all_enterprises_edges_by_id(self, client, enterprise_id):

        @retry(wait=wait_exponential(multiplier=self._config['multiplier'],
                                     min=self._config['min']),
               stop=stop_after_delay(self._config['stop_delay']))
        def get_all_enterprises_edges_by_id():
            body = {"enterpriseId": enterprise_id}

            response = requests.post(f"https://{client['host']}/portal/rest/enterprise/getEnterpriseEdges",
                                     data=json.dumps(body),
                                     headers=client['headers'],
                                     verify=False)
            return self._json_return(response.json())

        return get_all_enterprises_edges_by_id()

    def get_all_enterprise_names(self):
        enterprise_names = list()
        for client in self._clients:
            res = self.get_monitoring_aggregates(client)
            for enterprise in res["enterprises"]:
                enterprise_names.append({
                    "enterprise_name": enterprise["name"]
                })

        return enterprise_names

    def _json_return(self, response):
        if isinstance(response, dict):
            if 'error' in response.keys():
                if 'tokenError [expired session cookie]' in response['error']['message']:
                    self._logger.info(f'Response returned: {response}. Attempting to relogin')
                    self.instantiate_and_connect_clients()
                    raise Exception
                else:
                    self._logger.error(f'Error response returned: {response}')
        return response
