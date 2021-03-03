import time
from datetime import datetime

import asyncio
from shortuuid import uuid

from application.repositories import EdgeIdentifier
from application.repositories import nats_error_response


class VelocloudRepository:

    def __init__(self, config, logger, event_bus, notifications_repository):
        self._config = config
        self._logger = logger
        self._event_bus = event_bus
        self._notifications_repository = notifications_repository

    async def get_all_velo_edges(self):
        start_time = time.time()

        self._logger.info("Getting list of all velo edges")
        edge_list = await self.get_edges()
        self._logger.info(f"Got all edges from all velos. Took {(time.time() - start_time) // 60} minutes")

        self._logger.info("Getting list of logical IDs by each velo edge")
        logical_ids_by_edge_list = await self._get_logical_id_by_edge_list(edge_list)
        self._logger.info(f"Got all logical IDs by each velo edge. Took {(time.time() - start_time) // 60} minutes")

        self._logger.info(f"Mapping edges to serials...")
        edges_with_serial = await self._get_all_serials(edge_list, logical_ids_by_edge_list)
        self._logger.info(f"Amount of edges: {len(edges_with_serial)}")
        self._logger.info(f"Finished building velos + serials map. Took {(time.time() - start_time) // 60} minutes")

        return edges_with_serial

    async def _get_all_serials(self, edge_list, logical_ids_by_edge_list):
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

            logical_id_list = next((logical_id_edge for logical_id_edge in logical_ids_by_edge_list
                                   if logical_id_edge['host'] == edge['host']
                                   if logical_id_edge['enterprise_id'] == edge['enterpriseId']
                                   if logical_id_edge['edge_id'] == edge['edgeId']), None)
            logical_id = []
            if logical_id_list is not None:
                logical_id = logical_id_list['logical_id']

            edges_with_serials.append({
                'edge': edge_full_id,
                'serial_number': serial_number,
                'last_contact': last_contact,
                'logical_ids': logical_id
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
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def _get_all_enterprise_edges(self, host, enterprise_id, rpc_timeout=300):
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {
                'host': host,
                'enterprise_id': enterprise_id
            },
        }

        try:
            self._logger.info(f"Getting all edges from Velocloud host {host} and enterprise ID {enterprise_id}...")
            response = await self._event_bus.rpc_request("request.enterprises.edges", request, timeout=rpc_timeout)
            self._logger.info(f"Got all edges from Velocloud host {host} and enterprise ID {enterprise_id}!")
        except Exception as e:
            err_msg = f'An error occurred when requesting edge list from host {host} and enterprise ' \
                      f'ID {enterprise_id} -> {e}'
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status not in range(200, 300):
                err_msg = (
                    f'Error while retrieving edge list in {self._config.ENVIRONMENT_NAME.upper()} '
                    f'environment: Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

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

    async def _get_logical_id_by_edge_list(self, edge_list):
        host_to_enterprise_id = {}
        for edge in edge_list:
            host = edge['host']
            host_to_enterprise_id.setdefault(host, set())
            host_to_enterprise_id[host].add(edge['enterpriseId'])

        logical_id_by_edge_full_id_list = []
        for host in host_to_enterprise_id:
            for enterprise in host_to_enterprise_id[host]:
                enterprise_edge_list = await self._get_all_enterprise_edges(host, enterprise, rpc_timeout=90)
                if enterprise_edge_list['status'] not in range(200, 300):
                    self._logger.error(f'Error could not get enterprise edges of enterprise {enterprise}')
                    continue
                for edge in enterprise_edge_list['body']:
                    edge_full_id_and_logical_id = {
                        'host': host,
                        'enterprise_id': enterprise,
                        'edge_id': edge['id'],
                        'logical_id': []
                    }
                    for link in edge["links"]:
                        logical_id_dict = {'interface_name': link['interface'], 'logical_id': link['logicalId']}
                        edge_full_id_and_logical_id['logical_id'].append(logical_id_dict)
                    logical_id_by_edge_full_id_list.append(edge_full_id_and_logical_id)

        return logical_id_by_edge_full_id_list

    async def get_edges(self):
        edge_links_list = await self.get_all_edges_links()
        return self.extract_edge_info(edge_links_list['body'])
