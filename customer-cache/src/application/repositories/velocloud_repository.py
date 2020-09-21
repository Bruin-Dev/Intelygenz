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

        self._semaphore = asyncio.BoundedSemaphore(self._config.REFRESH_CONFIG['semaphore'])

    async def get_all_velo_edges(self):
        start_time = time.time()

        self._logger.info("Getting list of all velo edges")
        velo_servers = self._config.REFRESH_CONFIG["velo_servers"]
        edge_list = await self._get_all_edge_lists_parallel(velo_servers)
        self._logger.info(f"Got all edges from all velos. Took {(time.time() - start_time) // 60} minutes")

        self._logger.info(f"Mapping edges to serials...")
        edges_with_serial = await self._get_all_serials_in_parallel(edge_list)
        self._logger.info(f"Amount of edges: {len(edges_with_serial)}")
        self._logger.info(f"Finished building velos + serials map. Took {(time.time() - start_time) // 60} minutes")

        return edges_with_serial

    async def _get_all_edge_lists_parallel(self, velo_servers):
        edge_list = []

        tasks = [self.__get_edge_status_with_semaphore(edge) for edge in edge_list]
        responses = await asyncio.gather(*tasks)
        for velo_server in velo_servers:
            response = await self.get_edges(velo_server)
            responses.append(response)

        for response in responses:
            if response['status'] not in range(200, 300):
                continue
            edge_list = edge_list + response['body']

        return [
            edge
            for edge in edge_list
            if edge not in self._config.REFRESH_CONFIG["blacklisted_edges"]
        ]

    async def __get_edge_status_with_semaphore(self, edge: dict):
        async with self._semaphore:
            return await self.get_edge_status(edge)

    async def _get_all_serials_in_parallel(self, edge_list):
        edges_with_serials = []

        tasks = [self.__get_edge_status_with_semaphore(edge) for edge in edge_list]
        responses = await asyncio.gather(*tasks)

        for response in responses:
            if response['status'] not in range(200, 300):
                continue

            response_body = response['body']
            edge_full_id = response_body['edge_id']
            serial_number = response_body["edge_info"]['edges'].get('serialNumber')
            last_contact = response_body["edge_info"]['edges'].get('lastContact')

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
            if not filter_:
                self._logger.info("Getting list of all edges from Velocloud...")
            else:
                self._logger.info(f"Getting list of edges from Velocloud using filter {filter_}...")

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
                    f'Error while retrieving edge list in {self._config.ENVIRONMENT_NAME.upper()} '
                    f'environment: Error {response_status} - {response_body}'
                )

        if err_msg:
            await self._notify_error(err_msg)

        return response

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
                    f'{self._config.ENVIRONMENT_NAME.upper()} environment: Error {response_status} - {response_body}'
                )

        if err_msg:
            await self._notify_error(err_msg)

        return response

    async def _notify_error(self, err_msg):
        self._logger.error(err_msg)
        slack_message = {'request_id': uuid(), 'message': err_msg}
        await self._event_bus.rpc_request("notification.slack.request", slack_message, timeout=10)
