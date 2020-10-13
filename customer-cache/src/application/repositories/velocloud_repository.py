import time
from datetime import datetime

import asyncio
from shortuuid import uuid

from application.repositories import EdgeIdentifier
from application.repositories import nats_error_response


class VelocloudRepository:

    def __init__(self, config, logger, event_bus):
        self._config = config
        self._logger = logger
        self._event_bus = event_bus

    async def get_all_velo_edges(self):
        start_time = time.time()

        self._logger.info("Getting list of all velo edges")
        edge_list = await self.get_edges()
        self._logger.info(f"Got all edges from all velos. Took {(time.time() - start_time) // 60} minutes")

        self._logger.info(f"Mapping edges to serials...")
        edges_with_serial = await self._get_all_serials(edge_list)
        self._logger.info(f"Amount of edges: {len(edges_with_serial)}")
        self._logger.info(f"Finished building velos + serials map. Took {(time.time() - start_time) // 60} minutes")

        return edges_with_serial

    async def _get_all_serials(self, edge_list):
        edges_with_serials = []

        for edge in edge_list:
            edge_full_id = {
                'host': edge['host'],
                'enterprise_id': edge['enterpriseId'],
                'edge_id': edge['edgeId']
            }
            serial_number = edge.get('edgeSerialNumber')
            last_contact = edge.get('edgeLastContact')

            if last_contact == '0000-00-00 00:00:00' or last_contact is None:
                self._logger.info(f"Edge {EdgeIdentifier(**edge_full_id)} lastContact has an invalid value: "
                                  f"{last_contact}")
                continue
            if not serial_number:
                self._logger.info(f"Edge {EdgeIdentifier(**edge_full_id)} doesn't have a serial")
                continue

            edges_with_serials.append({
                'edge': edge_full_id,
                'serial_number': serial_number,
                'last_contact': last_contact,
            })

        return edges_with_serials

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
        edges_by_edge_identifier = {}
        for link in links_with_edge_info:
            edge_full_id = {
                'host': link['host'],
                'enterprise_id': link['enterpriseId'],
                'edge_id': link['edgeId']
            }
            edge_identifier = EdgeIdentifier(**edge_full_id)

            blacklist_edges = self._config.REFRESH_CONFIG["blacklisted_edges"]
            if edge_full_id in blacklist_edges:
                self._logger.info(f"Edge {edge_identifier} is in blacklist. Skipping...")
                continue

            if not link['edgeId']:
                self._logger.info(f"Edge {edge_identifier} doesn't have any ID. Skipping...")
                continue

            edges_by_edge_identifier.setdefault(
                edge_identifier,
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

        edges = list(edges_by_edge_identifier.values())
        return edges

    async def get_edges(self):
        edge_links_list = await self.get_all_edges_links()
        return self.extract_edge_info(edge_links_list['body'])

    async def _notify_error(self, err_msg):
        self._logger.error(err_msg)
        slack_message = {'request_id': uuid(), 'message': err_msg}
        await self._event_bus.rpc_request("notification.slack.request", slack_message, timeout=10)
