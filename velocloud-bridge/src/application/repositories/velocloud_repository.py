class VelocloudRepository:
    _config = None
    _clients = None
    _velocloud_client = None
    _logger = None

    def __init__(self, config, logger, velocloud_client):
        self._config = config.VELOCLOUD_CONFIG
        self._logger = logger
        self._velocloud_client = velocloud_client

    def connect_to_all_servers(self):
        self._logger.info('Instantiating and connecting clients in velocloud bridge')
        self._velocloud_client.instantiate_and_connect_clients()

    def get_all_enterprises_edges_with_host(self, msg):
        self._logger.info('Getting all enterprises edges with host')
        response = self._velocloud_client.get_all_enterprises_edges_with_host()
        if response["status"] not in range(200, 300):
            return {"body": response["body"], "status": response["status"]}
        status = response["status"]
        edges_by_enterprise = response["body"]
        if len(msg['filter']) > 0:

            edges_by_enterprise = [edge for edge in response["body"]
                                   for filter_edge in msg['filter']
                                   if edge['host'] == filter_edge['host']
                                   if edge['enterprise_id'] in filter_edge['enterprise_ids'] or len(filter_edge['enterprise_ids']) is 0]

        return {"body": edges_by_enterprise, "status": status}

    def get_edge_information(self, edge):
        edge_information = self._velocloud_client.get_edge_information(edge)
        if edge_information["status"] not in range(200, 300):
            self._logger.error(f"Error {edge_information['status']} edge_information")

        return edge_information

    def get_link_information(self, edge, interval):
        self._logger.info(f'Getting link information from edge:{edge["edge_id"]} in '
                          f'enterprise:{edge["enterprise_id"]} from host:{edge["host"]}')
        link_status = []
        response = self._velocloud_client.get_link_information(edge, interval)

        if response["status"] not in range(200, 300):
            self._logger.error(f"Error {response['status'], response['body']}")
            return {"body": response["body"], "status": response["status"]}

        links = response["body"]
        response_link_service_group = self._velocloud_client.get_link_service_groups_information(edge, interval)

        if response_link_service_group["status"] not in range(200, 300):
            self._logger.error(f"Error {response_link_service_group['status'], response['body']}")
            return {"body": link_status, "status": response_link_service_group["status"]}

        link_service_group = response_link_service_group["body"]

        if links is not None:
            for link in links:
                for link_service in link_service_group:
                    if link['linkId'] == link_service['linkId']:
                        link['serviceGroups'] = link_service['serviceGroups']
                        break
                if link['link']['backupState'] in ('UNCONFIGURED', 'ACTIVE'):
                    link_status.append(link)

        elif links is None:
            return {"body": link_status, "status": response["status"]}

        return {"body": link_status, "status": response["status"]}

    def get_enterprise_information(self, edge):
        enterprise_info = self._velocloud_client.get_enterprise_information(edge)
        if enterprise_info["status"] not in range(200, 300):
            self._logger.error(f"Error {enterprise_info['status']}, error: {enterprise_info['body']}")
            return {"body": None, "status": enterprise_info["status"]}

        body = enterprise_info["body"]
        name = body.get("name") if isinstance(body, dict) else None
        if enterprise_info['status'] in range(200, 300) and name:
            return {"body": name, "status": enterprise_info["status"]}
        else:
            return {"body": enterprise_info["body"], "status": enterprise_info["status"]}

    def get_all_edge_events(self, edge, start, end, limit, filter_events_status_list):
        self._logger.info(f'Getting events from edge:{edge["edge_id"]} from time:{start} to time:{end}')

        response = self._velocloud_client.get_all_edge_events(edge, start, end, limit)

        if response["status"] not in range(200, 300):
            return response

        full_events = response["body"]

        if filter_events_status_list is None:
            response["body"] = full_events["data"]
            return response
        else:
            event_list = [event for event in full_events["data"] if event['event'] in filter_events_status_list]
            response["body"] = event_list
            return response

    def get_all_enterprise_names(self, msg):
        self._logger.info('Getting all enterprise names')
        enterprises = self._velocloud_client.get_all_enterprise_names()

        if enterprises["status"] not in range(200, 300):
            self._logger.error(f"Error {enterprises['status']}, error: {enterprises['body']}")
            return {"body": enterprises["body"], "status": enterprises["status"]}

        enterprise_names = [e["enterprise_name"] for e in enterprises["body"]]

        if len(msg['filter']) > 0:
            enterprise_names = [
                e_name for e_name in enterprise_names
                for filter_enterprise in msg['filter']
                if e_name == filter_enterprise
            ]

        return {"body": enterprise_names, "status": enterprises["status"]}
