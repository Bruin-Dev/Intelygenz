import json
from datetime import datetime
from typing import List

from pytz import utc
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

    async def get_edge_events(self, edge_full_id: dict, from_: datetime, to: datetime, event_types: list = None):
        err_msg = None

        if not event_types:
            event_types = ['EDGE_UP', 'EDGE_DOWN', 'LINK_ALIVE', 'LINK_DEAD']

        request = {
            'request_id': uuid(),
            'body': {
                'edge': edge_full_id,
                'start_date': from_,
                'end_date': to,
                'filter': event_types,
            },
        }

        try:
            self._logger.info(
                f"Getting events of edge {json.dumps(edge_full_id)} having any type of {event_types} that took place "
                f"between {from_} and {to} from Velocloud..."
            )
            response = await self._event_bus.rpc_request("alert.request.event.edge", request, timeout=180)
            self._logger.info(
                f"Got events of edge {json.dumps(edge_full_id)} having any type in {event_types} that took place "
                f"between {from_} and {to} from Velocloud!"
            )
        except Exception as e:
            err_msg = (
                f'An error occurred when requesting edge events from Velocloud for edge '
                f'{json.dumps(edge_full_id)} -> {e}'
            )
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status not in range(200, 300):
                err_msg = (
                    f'Error while retrieving events of edge {json.dumps(edge_full_id)} having any type in '
                    f'{event_types} that took place between {from_} and {to} in '
                    f'{self._config.TRIAGE_CONFIG["environment"].upper()} environment: '
                    f'Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def get_network_enterprises(self, velocloud_host: str, *, enterprise_ids: List[int] = None):
        err_msg = None

        if not enterprise_ids:
            enterprise_ids = []

        request = {
            "request_id": uuid(),
            "body": {
                'host': velocloud_host,
                'enterprise_ids': enterprise_ids,
            },
        }

        try:
            if enterprise_ids:
                self._logger.info(
                    f"Getting network information for all edges belonging to enterprises "
                    f"{', '.join(map(str, enterprise_ids))} in host {velocloud_host}..."
                )
            else:
                self._logger.info(
                    "Getting network information for all edges belonging to all enterprises in host "
                    f"{velocloud_host}..."
                )
            response = await self._event_bus.rpc_request("request.network.enterprise.edges", request, timeout=30)
        except Exception as e:
            err_msg = f'An error occurred when requesting network info from Velocloud host {velocloud_host} -> {e}'
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status in range(200, 300):
                if enterprise_ids:
                    self._logger.info(
                        f"Got network information for all edges belonging to enterprises "
                        f"{', '.join(map(str, enterprise_ids))} in host {velocloud_host}!"
                    )
                else:
                    self._logger.info(
                        f"Got network information for all edges belonging to all enterprises in host {velocloud_host}!"
                    )
            else:
                err_msg = (
                    f'Error while retrieving network info from Velocloud host {velocloud_host} in '
                    f'{self._config.ENVIRONMENT_NAME.upper()} environment: Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def get_edges_for_triage(self):
        all_edges = []
        for host in self._config.TRIAGE_CONFIG["velo_hosts"]:
            response = await self.get_links_with_edge_info(velocloud_host=host)
            if response['status'] not in range(200, 300):
                self._logger.info(f"Error: could not retrieve edges links by host: {host}")
                continue
            all_edges += response['body']
        links_grouped_by_edge = self.group_links_by_edge(all_edges)
        return links_grouped_by_edge

    async def get_last_edge_events(self, edge_full_id: dict, since: datetime, event_types: list = None):
        current_datetime = datetime.now(utc)

        return await self.get_edge_events(edge_full_id, from_=since, to=current_datetime, event_types=event_types)

    async def get_last_down_edge_events(self, edge_full_id: dict, since: datetime):
        event_types = ['EDGE_DOWN', 'LINK_DEAD']

        return await self.get_last_edge_events(edge_full_id, since=since, event_types=event_types)

    def group_links_by_edge(self, links_with_edge_info: list) -> list:
        edges_by_serial_number = {}

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
                self._logger.info(
                    f"Edge {edge_name} in host {velocloud_host} and enterprise {enterprise_name} (ID: {enterprise_id}) "
                    f"has never been activated. Skipping..."
                )
                continue

            edges_by_serial_number.setdefault(
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
                    'edgeSerialNumber': serial_number,
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

            edges_by_serial_number[serial_number]["links"].append(link_info)

        edges = list(edges_by_serial_number.values())
        return edges
