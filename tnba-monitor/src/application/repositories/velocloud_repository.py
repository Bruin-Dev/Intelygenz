from shortuuid import uuid

from application.repositories import nats_error_response


class VelocloudRepository:
    def __init__(self, event_bus, logger, config, notifications_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._config = config
        self._notifications_repository = notifications_repository

    async def get_links_with_edge_info(self, velocloud_host: str):
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {
                'host': velocloud_host,
            },
        }

        try:
            self._logger.info(f"Getting links with edge info from Velocloud for host {velocloud_host}...")
            response = await self._event_bus.rpc_request("get.links.with.edge.info", request, timeout=30)
        except Exception as e:
            err_msg = f'An error occurred when requesting edge list from Velocloud -> {e}'
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status in range(200, 300):
                self._logger.info(f"Got links with edge info from Velocloud for host {velocloud_host}!")
            else:
                err_msg = (
                    f'Error while retrieving links with edge info in {self._config.ENVIRONMENT_NAME.upper()} '
                    f'environment: Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def get_edges_for_tnba_monitoring(self):
        all_edges = []
        for host in self._config.MONITOR_CONFIG["velo_filter"]:
            response = await self.get_links_with_edge_info(velocloud_host=host)
            if response['status'] not in range(200, 300):
                self._logger.info(f"Error: could not retrieve edges links by host: {host}")
                continue
            all_edges += response['body']
        links_grouped_by_edge = self.group_links_by_serial(all_edges)
        return links_grouped_by_edge

    @staticmethod
    def group_links_by_serial(links_with_edge_info: list) -> list:
        edges_by_serial = {}

        for link in links_with_edge_info:
            if not link['edgeId']:
                continue

            serial_number = link['edgeSerialNumber']

            edges_by_serial.setdefault(
                serial_number,
                {
                    'host': link['host'],
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
                    "links": [],
                }
            )

            link_info = {
                'displayName': link['displayName'],
                'isp': link['isp'],
                'interface': link['interface'],
                'internalId': link['internalId'],
                'linkState': link['linkState'],
                'linkLastActive': link['linkLastActive'],
                'linkVpnState': link['linkVpnState'],
                'linkId': link['linkId'],
                'linkIpAddress': link['linkIpAddress'],
            }

            edges_by_serial[serial_number]["links"].append(link_info)

        edges = list(edges_by_serial.values())
        return edges
