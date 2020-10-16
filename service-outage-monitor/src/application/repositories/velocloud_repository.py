from datetime import datetime
from typing import Dict

from pytz import utc
from shortuuid import uuid

from application.repositories import nats_error_response
from application.repositories import EdgeIdentifier


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
        edge_identifier = EdgeIdentifier(**edge_full_id)

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
                f"Getting events of edge {edge_identifier} having any type of {event_types} that took place "
                f"between {from_} and {to} from Velocloud..."
            )
            response = await self._event_bus.rpc_request("alert.request.event.edge", request, timeout=180)
            self._logger.info(
                f"Got events of edge {edge_identifier} having any type in {event_types} that took place "
                f"between {from_} and {to} from Velocloud!"
            )
        except Exception as e:
            err_msg = f'An error occurred when requesting edge events from Velocloud for edge {edge_identifier} -> {e}'
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status not in range(200, 300):
                err_msg = (
                    f'Error while retrieving events of edge {edge_identifier} having any type in {event_types} that '
                    f'took place between {from_} and {to} in {self._config.TRIAGE_CONFIG["environment"].upper()}'
                    f'environment: Error {response_status} - {response_body}'
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

    @staticmethod
    def group_links_by_edge(links_with_edge_info: list) -> list:
        edges_by_edge_identifier = {}

        for link in links_with_edge_info:
            if not link['edgeId']:
                continue

            edge_full_id = {
                'host': link['host'],
                'enterprise_id': link['enterpriseId'],
                'edge_id': link['edgeId']
            }
            edge_identifier = EdgeIdentifier(**edge_full_id)

            edges_by_edge_identifier.setdefault(
                edge_identifier,
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

            edges_by_edge_identifier[edge_identifier]["links"].append(link_info)

        edges = list(edges_by_edge_identifier.values())
        return edges
