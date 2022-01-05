import json
import time

from shortuuid import uuid

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
        edges_with_config = []
        for edge in edges_with_serial:
            edges_with_config.append(await self.add_edge_config(edge))
        self._logger.info(f"Finished building velos + serials map. Took {(time.time() - start_time) // 60} minutes")

        return edges_with_config

    async def _get_all_serials(self, edge_list, logical_ids_by_edge_list):
        edges_with_serials = []

        for edge in edge_list:
            edge_full_id = {
                'host': edge['host'],
                'enterprise_id': edge['enterpriseId'],
                'edge_id': edge['edgeId']
            }
            serial_number = edge.get('edgeSerialNumber')
            ha_serial_number = edge.get('edgeHASerialNumber')
            last_contact = edge.get('edgeLastContact')
            edge_name = edge.get('edgeName')

            logical_id_list = next((logical_id_edge for logical_id_edge in logical_ids_by_edge_list
                                    if logical_id_edge['host'] == edge['host']
                                    if logical_id_edge['enterprise_id'] == edge['enterpriseId']
                                    if logical_id_edge['edge_id'] == edge['edgeId']), None)
            logical_id = []
            if logical_id_list is not None:
                logical_id = logical_id_list['logical_id']

            edges_with_serials.append({
                'edge': edge_full_id,
                'edge_name': edge_name,
                'serial_number': serial_number,
                'ha_serial_number': ha_serial_number,
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

    async def get_links_configuration(self, edge):
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": edge
        }

        try:
            self._logger.info(f"Getting links configuration for edge {edge}...")
            response = await self._event_bus.rpc_request("request.links.configuration", request, timeout=30)
        except Exception as e:
            err_msg = f'An error occurred when requesting links configuration for edge {edge} -> {e}'
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status not in range(200, 300):
                err_msg = (
                    f'Error while retrieving links configuration for edge {edge} in '
                    f'{self._config.ENVIRONMENT_NAME.upper()} environment: Error {response_status} - {response_body}'

                )
            else:
                self._logger.info(f"Got links configuration for edge {edge}!")

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
        edges_by_serial = {}
        for link in links_with_edge_info:
            velocloud_host = link['host']
            enterprise_name = link['enterpriseName']
            enterprise_id = link['enterpriseId']
            edge_name = link['edgeName']
            edge_state = link['edgeState']
            serial_number = link['edgeSerialNumber']

            if edge_state is None:
                self._logger.info(
                    f"Edge in host {velocloud_host} and enterprise {enterprise_name} (ID: {enterprise_id}) "
                    f"has an invalid state. Skipping..."
                )
                continue

            if edge_state == 'NEVER_ACTIVATED':
                if velocloud_host == 'metgsavco-ic1.fedmettel.net':
                    # Do not leak edge name if it's a GSA edge
                    self._logger.info(
                        f"Edge {link['edgeId']} in host {velocloud_host} and enterprise {enterprise_name}"
                        f"(ID: {enterprise_id}) has never been activated. Skipping..."
                    )
                else:
                    self._logger.info(
                        f"Edge {edge_name} in host {velocloud_host} and enterprise {enterprise_name}"
                        f"(ID: {enterprise_id}) has never been activated. Skipping..."
                    )
                continue

            edge_full_id = {
                'host': link['host'],
                'enterprise_id': enterprise_id,
                'edge_id': link['edgeId']
            }
            blacklist_edges = self._config.REFRESH_CONFIG["blacklisted_edges"]
            if edge_full_id in blacklist_edges:
                self._logger.info(
                    f"Edge {json.dumps(edge_full_id)} (serial: {serial_number}) is in blacklist. Skipping..."
                )
                continue

            edge = {
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

            if edge['host'] == 'metgsavco-ic1.fedmettel.net':
                edge['edgeName'] = None

            edges_by_serial.setdefault(serial_number, edge)

        edges = list(edges_by_serial.values())
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

    async def add_edge_config(self, edge):
        edge['links_configuration'] = []

        edge_request = edge['edge']
        configuration_response = await self.get_links_configuration(edge_request)
        if configuration_response['status'] not in range(200, 300):
            self._logger.error(f'Error while getting links configuration for edge {edge_request}')
            return edge

        for link in configuration_response['body']:
            edge['links_configuration'].append(
                {
                    'interfaces': link['interfaces'],
                    'mode': link['mode'],
                    'type': link['type'],
                }
            )
        return edge
