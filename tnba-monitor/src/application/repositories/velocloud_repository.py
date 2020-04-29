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
                    f'Error while retrieving edge list in {self._config.ENVIRONMENT.upper()} '
                    f'environment: Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

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
                    f'Error while retrieving status of edge {edge_identifier} in {self._config.ENVIRONMENT.upper()} '
                    f'environment: Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def get_edges_for_tnba_monitoring(self):
        monitoring_filter = self._config.MONITOR_CONFIG['velo_filter']

        return await self.get_edges(filter_=monitoring_filter)
