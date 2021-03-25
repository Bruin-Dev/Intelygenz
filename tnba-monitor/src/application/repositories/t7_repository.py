from shortuuid import uuid
from typing import List

from application.repositories import nats_error_response


class T7Repository:
    def __init__(self, event_bus, logger, config, notifications_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._config = config
        self._notifications_repository = notifications_repository

    async def get_prediction(self, ticket_id: int, ticket_rows: List[dict], assets_to_predict: List[str]) -> dict:
        err_msg = None

        request = {
            'request_id': uuid(),
            'body': {
                'ticket_id': ticket_id,
                'ticket_rows': ticket_rows,
                'assets_to_predict': assets_to_predict,
            },
        }

        try:
            self._logger.info(f'Claiming T7 prediction for ticket {ticket_id}...')
            response = await self._event_bus.rpc_request("t7.prediction.request", request, timeout=60)
            self._logger.info(f'Got T7 prediction for ticket {ticket_id}!')
        except Exception as e:
            err_msg = f'An error occurred when claiming T7 prediction for ticket {ticket_id}. Error: {e}'
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status not in range(200, 300):
                err_msg = (
                    f'Error while claiming T7 prediction for ticket {ticket_id} in {self._config.ENVIRONMENT.upper()} '
                    f'environment. Error: Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def post_live_automation_metrics(self, ticket_id: int, asset_id: str, automated_successfully: bool) -> dict:
        err_msg = None

        request = {
            'request_id': uuid(),
            'body': {
                "ticket_id": ticket_id,
                "asset_id": asset_id,
                "automated_successfully": automated_successfully
            },
        }

        try:
            self._logger.info(f'Posting live metric for ticket {ticket_id} to T7...')
            response = await self._event_bus.rpc_request("t7.live.automation.metrics", request, timeout=60)
        except Exception as e:
            err_msg = f'An error occurred when posting live metrics for ticket {ticket_id} to T7. Error: {e}'
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status in range(200, 300):
                self._logger.info(f'Live metrics posted for ticket {ticket_id}!')
            else:
                err_msg = (
                        f'Error when posting live metrics for ticket {ticket_id} to T7 in '
                        f'{self._config.ENVIRONMENT.upper()} '
                        f'environment. Error: Error {response_status} - {response_body}'
                    )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response
