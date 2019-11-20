import json

import requests


# TODO NOTES FOR THE FUTURE
#  currently edge_ids look like
#  {"host": "metvco04.mettel.net", "enterprise_id": 27, "edge_id": 106}


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
        # TODO login each host and return a dict with host name and a
        #  header dict with the cookie/Content-Type/cache-control
        self._logger.info(f'Logging in host: {host} to velocloud')

        client = dict()
        client['host'] = host
        client['headers'] = self._create_headers_by_host(host, user, password)

        return client

    def _create_headers_by_host(self, host, user, password):
        credentials = {
            "username": user,
            "password": password
        }
        response = requests.post(f"https://{host}/portal/rest/login/operatorLogin",
                                 headers={"Content-Type": "application/json"},
                                 data=credentials,
                                 allow_redirects=False,
                                 verify=False)

        # # DEBUG PURPOSES ONLY # #
        self._logger.info("# # DEBUG PURPOSES ONLY # #")
        self._logger.info(response.status_code)
        self._logger.info(response.headers)
        ###########################

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

    def _get_header_by_host(self, host):
        host_client = [client
                       for client in self._clients
                       if host in
                       client['host']][0]
        return host_client

    def get_edge_information(self, edge):
        # TODO Make get edge call
        target_host_client = self._get_header_by_host(edge["host"])
        edgeids = {"enterpriseId": edge["enterprise_id"], "id": edge["edge_id"]}
        response = requests.post(f"https://{edge['host']}/portal/rest/edge/getEdge",
                                 data=json.dumps(edgeids),
                                 headers=target_host_client['headers'],
                                 verify=False)
        # # DEBUG PURPOSES ONLY # #
        self._logger.info("# # DEBUG PURPOSES ONLY # #")
        self._logger.info(response.status_code)
        self._logger.info(response.json())
        self._logger.info(response.headers)
        ###########################

        return response.json()

    def get_link_information(self, edge, interval):
        # TODO Make get link call
        target_host_client = self._get_header_by_host(edge["host"])
        edgeids = {"enterpriseId": edge["enterprise_id"], "id": edge["edge_id"], "interval": interval}
        response = requests.post(f"https://{edge['host']}/portal/rest/metrics/getEdgeLinkMetrics",
                                 data=json.dumps(edgeids),
                                 headers=target_host_client['headers'],
                                 verify=False)

        # # DEBUG PURPOSES ONLY # #
        self._logger.info("# # DEBUG PURPOSES ONLY # #")
        self._logger.info(response.status_code)
        self._logger.info(response.json())
        self._logger.info(response.headers)
        ###########################

        return response.json()

    def get_link_service_groups_information(self, edge):
        # TODO Make link service call
        target_host_client = self._get_header_by_host(edge["host"])
        edgeids = {"enterpriseId": edge["enterprise_id"], "id": edge["edge_id"]}
        response = requests.post(f"https://{edge['host']}/portal/rest/metrics/getEdgeAppLinkMetrics",
                                 data=json.dumps(edgeids),
                                 headers=target_host_client['headers'],
                                 verify=False)
        # # DEBUG PURPOSES ONLY # #
        self._logger.info("# # DEBUG PURPOSES ONLY # #")
        self._logger.info(response.status_code)
        self._logger.info(response.json())
        self._logger.info(response.headers)
        ###########################

        return response.json()

    def get_enterprise_information(self, edge):
        # TODO Make enterprise info call
        target_host_client = self._get_header_by_host(edge["host"])
        body = {"enterpriseId": edge["enterprise_id"]}
        response = requests.post(f"https://{edge['host']}/portal/rest/enterprise/getEnterprise",
                                 data=json.dumps(body),
                                 headers=target_host_client['headers'],
                                 verify=False)
        # # DEBUG PURPOSES ONLY # #
        self._logger.info("# # DEBUG PURPOSES ONLY # #")
        self._logger.info(response.status_code)
        self._logger.info(response.json())
        self._logger.info(response.headers)
        ###########################

        return response.json()

    def get_all_edge_events(self, edge, start, end, limit):
        # TODO Make event call
        target_host_client = self._get_header_by_host(edge["host"])
        body = {"enterpriseId": edge["enterprise_id"],
                "interval": {"start": start, "end": end},
                "filter": {"limit": limit},
                "edgeId": [edge["edge_id"]]}

        response = requests.post(f"https://{edge['host']}/portal/rest/event/getEnterpriseEvents",
                                 data=json.dumps(body),
                                 headers=target_host_client['headers'],
                                 verify=False)
        # # DEBUG PURPOSES ONLY # #
        self._logger.info("# # DEBUG PURPOSES ONLY # #")
        self._logger.info(response.status_code)
        self._logger.info(response.json())
        self._logger.info(response.headers)
        ###########################

        return response.json()

    def get_all_enterprises_edges_with_host(self):
        # TODO for client in clients
        #  clients['host'] is BASE_URL and
        #  clients['header'] is header
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

        # # # DEBUG PURPOSES ONLY # #
        # self._logger.info("# # DEBUG PURPOSES ONLY # #")
        # self._logger.info(edges_by_enterprise_and_host)
        # ###########################

        return edges_by_enterprise_and_host

    def get_all_hosts_edge_count(self):
        sum = 0
        for client in self._clients:
            res = self.get_monitoring_aggregates(client)
            sum += res["edgeCount"]

        # # DEBUG PURPOSES ONLY # #
        self._logger.info("# # DEBUG PURPOSES ONLY # #")
        self._logger.info(sum)
        ###########################

        return sum

    def get_monitoring_aggregates(self, client):

        response = requests.post(f"https://{client['host']}/portal/rest/monitoring/getAggregates",
                                 data={},
                                 headers=client['headers'],
                                 verify=False)

        # # DEBUG PURPOSES ONLY # #
        self._logger.info("# # DEBUG PURPOSES ONLY # #")
        self._logger.info(response.status_code)
        self._logger.info(response.json())
        self._logger.info(response.headers)
        ###########################

        return response.json()

    def get_all_enterprises_edges_by_id(self, client, enterprise_id):
        body = {"enterpriseId": enterprise_id}

        response = requests.post(f"https://{client['host']}/portal/rest/enterprise/getEnterpriseEdges",
                                 data=json.dumps(body),
                                 headers=client['headers'],
                                 verify=False)

        # # # DEBUG PURPOSES ONLY # #
        # self._logger.info("# # DEBUG PURPOSES ONLY # #")
        # self._logger.info(response.status_code)
        # self._logger.info(response.json())
        # self._logger.info(response.headers)
        # ###########################

        return response.json()
