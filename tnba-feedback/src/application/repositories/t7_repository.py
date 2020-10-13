from shortuuid import uuid

from application.repositories import nats_error_response


class T7Repository:
    def __init__(self, event_bus, logger, config, notifications_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._config = config
        self._notifications_repository = notifications_repository

    async def post_metrics(self, ticket_id: int, ticket_rows: list):
        err_msg = None

        request = {
            'request_id': uuid(),
            'body': {
                'ticket_id': ticket_id,
                'ticket_rows': ticket_rows

            },
        }

        try:
            self._logger.info(f'Posting metrics for ticket {ticket_id} to T7...')
            response = await self._event_bus.rpc_request("t7.automation.metrics", request, timeout=60)
            self._logger.info(f'Metrics posted for ticket {ticket_id}!')
        except Exception as e:
            err_msg = f'An error occurred when posting metrics for ticket {ticket_id} to T7. Error: {e}'
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status not in range(200, 300):
                err_msg = (
                    f'Error when posting metrics for ticket {ticket_id} to T7 in '
                    f'{self._config.TNBA_FEEDBACK_CONFIG["environment"].upper()} '
                    f'environment. Error: Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        elif response['kre_response']['status_code'] != 'SUCCESS':
            err_msg = (
                f'Error: Shadow testing KRE error posting metrics for ticket {ticket_id} to KRE in '
                f'{self._config.TNBA_FEEDBACK_CONFIG["environment"].upper()} '
                f'environment. Error: Error {response["kre_response"]["body"]}'
            )

            await self._notifications_repository.send_slack_message(err_msg)

        return response

    def tnba_note_in_task_history(self, task_history):
        task_history_tnba_filter = [task for task in task_history if task["Notes"] is not None
                                    if "TNBA" in task["Notes"]]
        if len(task_history_tnba_filter) > 0:
            return True

        return False
