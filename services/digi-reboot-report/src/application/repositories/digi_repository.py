from shortuuid import uuid
from datetime import datetime, timedelta
from pytz import utc, timezone
from application.repositories import nats_error_response


class DiGiRepository:

    def __init__(self, event_bus, logger, config, notifications_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._config = config
        self._notifications_repository = notifications_repository

    async def get_digi_recovery_logs(self):
        err_msg = None
        tz = timezone(self._config.TIMEZONE)
        start_date_time = datetime.now(tz) - timedelta(days=self._config.DIGI_CONFIG['days_of_digi_recovery_log'])
        request = {
            'request_id': uuid(),
            'body': {
                'start_date_time': start_date_time,
                'size': '999'
            },
        }

        try:
            self._logger.info(f'Getting DiGi recovery logs from '
                              f'{self._config.DIGI_CONFIG["days_of_digi_recovery_log"]} '
                              f'day(s) ago')
            response = await self._event_bus.rpc_request("get.digi.recovery.logs", request, timeout=90)
            self._logger.info(f'Got DiGi recovery logs from {self._config.DIGI_CONFIG["days_of_digi_recovery_log"]} '
                              f'day(s) ago')
        except Exception as e:
            err_msg = f'An error occurred when attempting to get DiGi recovery logs -> {e}'
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status not in range(200, 300):
                err_msg = (
                    f'Error while attempting to get DiGi recovery logs in '
                    f'{self._config.ENVIRONMENT_NAME.upper()} environment: '
                    f'Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response
