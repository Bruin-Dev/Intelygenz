from shortuuid import uuid

nats_error_response = {'body': None, 'status': 503}


class VelocloudRepository:
    def __init__(self, event_bus, logger, config, notifications_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._config = config
        self._notifications_repository = notifications_repository

    async def get_edges_links_by_host(self, host, rpc_timeout=300):
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {
                'host': host
            },
        }

        try:
            self._logger.info(f"Getting edges links from Velocloud for host {host}...")
            response = await self._event_bus.rpc_request("get.links.with.edge.info", request, timeout=rpc_timeout)
            self._logger.info("Got edges links from Velocloud!")
        except Exception as e:
            err_msg = f'An error occurred when requesting edge list from {host} -> {e}'
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status not in range(200, 300):
                err_msg = (
                    f'Error while retrieving edges links in {self._config.ENVIRONMENT_NAME.upper()} '
                    f'environment: Error {response_status} - {response_body}'
                )

        if err_msg:
            await self._notify_error(err_msg)

        return response

    async def get_all_edges_links(self):
        all_edges = []
        for host in self._config.VELOCLOUD_HOST:
            response = await self.get_edges_links_by_host(host=host)
            if response['status'] not in range(200, 300):
                self._logger.info(f"Error: could not retrieve edges links by host: {host}")
                continue
            all_edges += response['body']

        return_response = {
            "request_id": uuid(),
            'status': 200,
            'body': all_edges
        }
        return return_response

    def extract_edge_info(self, links_with_edge_info: list) -> list:
        edges_by_edge_serial = {}
        for link in links_with_edge_info:
            serial_number = link['edgeSerialNumber']

            if not link['edgeId']:
                self._logger.info(f"Edge {serial_number} doesn't have any ID. Skipping...")
                continue

            edges_by_edge_serial.setdefault(
                serial_number,
                {
                    'enterpriseName': link['enterpriseName'],
                    'enterpriseId': link['enterpriseId'],
                    'enterpriseProxyId': link['enterpriseProxyId'],
                    'enterpriseProxyName': link['enterpriseProxyName'],
                    'edgeName': link['edgeName'],
                    'edgeState': link['edgeState'],
                    'edgeSystemUpSince': link['edgeSystemUpSince'],
                    'edgeServiceUpSince': link['edgeServiceUpSince'],
                    'edgeLastContact': link['edgeLastContact'],
                    'edgeId': link['edgeId'],
                    'edgeSerialNumber': link['edgeSerialNumber'],
                    'edgeHASerialNumber': link['edgeHASerialNumber'],
                    'edgeModelNumber': link['edgeModelNumber'],
                    'edgeLatitude': link['edgeLatitude'],
                    'edgeLongitude': link['edgeLongitude'],
                    'host': link['host'],
                }
            )

        edges = list(edges_by_edge_serial.values())
        return edges

    async def get_edges(self):
        edge_links_list = await self.get_all_edges_links()
        return self.extract_edge_info(edge_links_list['body'])

    async def _notify_error(self, err_msg):
        self._logger.error(err_msg)
        await self._notifications_repository.send_slack_message(err_msg)
