from datetime import datetime

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

    async def get_edges(self, filter_: dict = None, *, rpc_timeout=300):
        err_msg = None

        if not filter_:
            filter_ = {}

        request = {
            "request_id": uuid(),
            "body": {
                'filter': filter_,
            },
        }

        try:
            self._logger.info("Getting list of edges from Velocloud...")
            response = await self._event_bus.rpc_request("edge.list.request", request, timeout=rpc_timeout)
            self._logger.info("Got list of edges from Velocloud!")
        except Exception as e:
            err_msg = f'An error occurred when requesting edge list from Velocloud -> {e}'
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status not in range(200, 300):
                err_msg = (
                    f'{self._config.MONITOR_CONFIG["environment"].upper()} environment: '
                    f'environment: Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def get_links_with_edge_info(self, host, rpc_timeout=300):
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {
                'host': host,
            },
        }

        try:
            self._logger.info("Getting list of link with edge info from Velocloud...")
            response = await self._event_bus.rpc_request("get.links.with.edge.info", request, timeout=rpc_timeout)
            self._logger.info("Got list of link with edge info from Velocloud!")
        except Exception as e:
            err_msg = f'An error occurred when requesting list of link with edge info from Velocloud -> {e}'
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status not in range(200, 300):
                err_msg = (
                    f'Error while retrieving list of link with edge info in '
                    f'{self._config.MONITOR_CONFIG["environment"].upper()} '
                    f'environment: Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def get_links_with_edge_info_for_triage(self):
        all_links_with_edge_info_list = []
        for host in self._config.TRIAGE_CONFIG['velo_hosts']:
            links_with_edge_info_for_host = await self.get_links_with_edge_info(host)
            links_with_edge_info_for_host_body = links_with_edge_info_for_host["body"]
            links_with_edge_info_for_host_status = links_with_edge_info_for_host["status"]

            if links_with_edge_info_for_host_status not in range(200, 300):
                continue
            all_links_with_edge_info_list = all_links_with_edge_info_list + links_with_edge_info_for_host_body

        return all_links_with_edge_info_list

    async def get_edge_status(self, edge_full_id: dict):
        err_msg = None
        edge_identifier = EdgeIdentifier(**edge_full_id)

        request = {
            "request_id": uuid(),
            "body": edge_full_id,
        }

        try:
            self._logger.info(f"Getting status of edge {edge_identifier} from Velocloud...")
            response = await self._event_bus.rpc_request("edge.status.request", request, timeout=120)
            self._logger.info(f"Got status of edge {edge_identifier} from Velocloud!")
        except Exception as e:
            err_msg = f'An error occurred when requesting status of edge {edge_identifier} from Velocloud -> {e}'
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status not in range(200, 300):
                err_msg = (
                    f'Error while retrieving status of edge {edge_identifier} in '
                    f'{self._config.MONITOR_CONFIG["environment"].upper()} environment: '
                    f'Error {response_status} - {response_body}'
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
        monitoring_filter = self._config.MONITOR_MAP_CONFIG["velo_filter"]

        return await self.get_edges(filter_=monitoring_filter)

    async def get_edges_for_outage_monitoring(self):
        monitoring_filter = self._config.MONITOR_CONFIG['velocloud_instances_filter']

        return await self.get_edges(filter_=monitoring_filter)

    async def get_last_edge_events(self, edge_full_id: dict, since: datetime, event_types: list = None):
        current_datetime = datetime.now(utc)

        return await self.get_edge_events(edge_full_id, from_=since, to=current_datetime, event_types=event_types)

    async def get_last_down_edge_events(self, edge_full_id: dict, since: datetime):
        event_types = ['EDGE_DOWN', 'LINK_DEAD']

        return await self.get_last_edge_events(edge_full_id, since=since, event_types=event_types)
