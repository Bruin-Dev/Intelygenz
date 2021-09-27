from typing import Dict
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
            err_msg = f'An error occurred when requesting edge list from Velocloud -> {e}'
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

    async def get_all_links_with_edge_info(self):
        all_edges = []
        for host in self._config.SITES_MONITOR_CONFIG['velo_servers']:
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

    def group_links_by_edge_serial(self, edge_links_list) -> Dict[str, dict]:
        result = {}
        for edge_link in edge_links_list:
            serial_number = edge_link['edgeSerialNumber']

            if not edge_link['edgeId']:
                self._logger.info(f"Edge {serial_number} without edgeId")
                continue

            result.setdefault(
                serial_number,
                {
                    'enterpriseName': edge_link['enterpriseName'],
                    'enterpriseId': edge_link['enterpriseId'],
                    'enterpriseProxyId': edge_link['enterpriseProxyId'],
                    'enterpriseProxyName': edge_link['enterpriseProxyName'],
                    'edgeName': edge_link['edgeName'],
                    'edgeState': edge_link['edgeState'],
                    'edgeSystemUpSince': edge_link['edgeSystemUpSince'],
                    'edgeServiceUpSince': edge_link['edgeServiceUpSince'],
                    'edgeLastContact': edge_link['edgeLastContact'],
                    'edgeId': edge_link['edgeId'],
                    'edgeSerialNumber': edge_link['edgeSerialNumber'],
                    'edgeHASerialNumber': edge_link['edgeHASerialNumber'],
                    'edgeModelNumber': edge_link['edgeModelNumber'],
                    'edgeLatitude': edge_link['edgeLatitude'],
                    'edgeLongitude': edge_link['edgeLongitude'],
                    'host': edge_link['host'],
                    "links": []
                }
            )

            if not edge_link['linkState']:
                self._logger.info(f"Edge [{serial_number}] with link interface {edge_link['interface']} "
                                  f"without state")
                continue

            edge_link_info = {
                'interface': edge_link['interface'],
                'internalId': edge_link['internalId'],
                'linkState': edge_link['linkState'],
                'linkLastActive': edge_link['linkLastActive'],
                'linkVpnState': edge_link['linkVpnState'],
                'linkId': edge_link['linkId'],
                'linkIpAddress': edge_link['linkIpAddress'],
                'displayName': edge_link['displayName'],
                'isp': edge_link['isp'],
            }

            result[serial_number]["links"].append(edge_link_info)

        return result

    async def _notify_error(self, err_msg):
        self._logger.error(err_msg)
        await self._notifications_repository.send_slack_message(err_msg)
