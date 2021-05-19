from typing import List


class VelocloudRepository:
    _config = None
    _clients = None
    _velocloud_client = None
    _logger = None

    def __init__(self, config, logger, velocloud_client):
        self._config = config.VELOCLOUD_CONFIG
        self._logger = logger
        self._velocloud_client = velocloud_client

    async def connect_to_all_servers(self):
        self._logger.info('Instantiating and connecting clients in velocloud bridge')
        await self._velocloud_client.instantiate_and_connect_clients()

    async def get_all_edge_events(self, edge, start, end, limit, filter_events_status_list):
        self._logger.info(f'Getting events from edge:{edge["edge_id"]} from time:{start} to time:{end}')

        response = await self._velocloud_client.get_all_edge_events(edge, start, end, limit)

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

    async def get_all_enterprise_names(self, msg):
        self._logger.info('Getting all enterprise names')
        enterprises = await self._velocloud_client.get_all_enterprise_names()

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

    async def get_links_with_edge_info(self, velocloud_host: str):
        links_with_edge_info_response = await self._velocloud_client.get_links_with_edge_info(velocloud_host)

        if links_with_edge_info_response['status'] not in range(200, 300):
            return links_with_edge_info_response

        for elem in links_with_edge_info_response['body']:
            elem['host'] = velocloud_host

        return links_with_edge_info_response

    async def get_links_metric_info(self, velocloud_host: str, interval: dict):
        links_metric_info_response = await self._velocloud_client.get_links_metric_info(velocloud_host, interval)

        if links_metric_info_response['status'] not in range(200, 300):
            return links_metric_info_response

        for elem in links_metric_info_response['body']:
            elem['link']['host'] = velocloud_host

        return links_metric_info_response

    async def get_enterprise_edges(self, host, enterprise_id):
        return await self._velocloud_client.get_enterprise_edges(host, enterprise_id)

    async def get_links_configuration(self, edge_full_id):
        config_response = {}

        config_stack_response = await self._velocloud_client.get_edge_configuration_stack(edge_full_id)
        if config_stack_response['status'] not in range(200, 300):
            config_response["status"] = config_stack_response['status']
            config_response["body"] = f'Bad status calling get_edge_configuration_stack. ' \
                                      f'Response {config_stack_response} for edge {edge_full_id}'
            return config_response

        config_stack = config_stack_response['body']
        if not config_stack:
            config_response["status"] = 404
            config_response["body"] = f'No config stack was found for edge {edge_full_id}'
            return config_response

        edge_config = [config for config in config_stack if config['name'] == 'Edge Specific Profile']
        if not edge_config:
            config_response["status"] = 404
            config_response["body"] = f'No specific config was found for edge {edge_full_id}'
            return config_response

        edge_config = edge_config[0]
        config_wan_module = [module for module in edge_config['modules'] if module['name'] == 'WAN']
        if not config_wan_module:
            config_response["status"] = 404
            config_response["body"] = f'No WAN module was found for edge {edge_full_id}'
            return config_response

        config_wan_module = config_wan_module[0]
        wan_module_data = config_wan_module['data']
        links_configuration = wan_module_data.get('links')
        if not links_configuration:
            config_response["status"] = 404
            config_response["body"] = f'No links configuration was found in WAN module of edge {edge_full_id}'
            return config_response

        config_response["status"] = 200
        config_response["body"] = links_configuration

        return config_response
