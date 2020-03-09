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
        return self._velocloud_client.get_all_enterprises_edges_with_host(msg["filter"])

    def get_edge_information(self, edge):
        return self._velocloud_client.get_edge_information(edge)

    def get_link_information(self, edge, interval):
        self._logger.info(f'Getting link information from edge:{edge["edge_id"]} in '
                          f'enterprise:{edge["enterprise_id"]} from host:{edge["host"]}')
        link_status = []
        response = self._velocloud_client.get_link_information(edge, interval)

        if response["status"] not in range(200, 300):
            return response

        links = response["body"]
        response_link_service_group = self._velocloud_client.get_link_service_groups_information(edge, interval)

        if response_link_service_group["status"] not in range(200, 300):
            self._logger.error(f"Error {response_link_service_group['status'], response['body']}")
            return {"body": response_link_service_group["body"], "status": response_link_service_group["status"]}

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
            return enterprise_info

        enterprise_info["body"] = enterprise_info["body"]["name"]
        return enterprise_info

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
