from igz.packages.eventbus.eventbus import EventBus
from shortuuid import uuid
from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from pytz import timezone
from datetime import datetime
from datetime import timedelta


class TNBAMonitor:
    # Poll all tickets given a list of bruin company ids (keys in a map of company_id: [serials]
    # For each ticket look if age is greater than 45 minutes
    # For each ticket look if in any detail there is a serial for that company ID
    # If there is detail with that serial and amount of times is lesser than max ask for prediction
    # If prediction is in automatable task list and is not the same as the last one, proceed with it
    # Call to prediction again with this prediction and amount of times

    def __init__(self, config, logger, event_bus: EventBus, scheduler, prediction_repository, ticket_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._scheduler = scheduler
        self._config = config
        self._prediction_repository = prediction_repository
        self._ticket_repository = ticket_repository

    async def start_tnba_automated_process(self, exec_on_start=False):
        self._logger.info('Scheduling TNBA automated process job...')
        next_run_time = undefined

        if exec_on_start:
            tz = timezone(self._config.TIMEZONE)
            next_run_time = datetime.now(tz)
            self._logger.info('TNBA automated process job is going to be executed immediately')

        try:
            self._scheduler.add_job(self._tnba_automated_process, 'interval',
                                    seconds=self._config.MONITORING_INTERVAL_SECONDS,
                                    next_run_time=next_run_time, replace_existing=False,
                                    id='_tnba_automated_process')
        except ConflictingIdError as conflict:
            self._logger.info(f'Skipping start of TNBA automated process job. Reason: {conflict}')

    async def _tnba_automated_process(self):
        valid_ticket_objects = await self._ticket_repository.get_all_valid_tickets_with_serial_and_detail()
        for valid_ticket_object in valid_ticket_objects:
            ticket_id = valid_ticket_object["ticket_id"]
            serial_number = valid_ticket_object["serial_number"]
            detail_id = valid_ticket_object["detail_id"]
            prediction = await self._prediction_repository.get_prediction(ticket_id, serial_number)

            # Check if ticket was resolved between getting the ticket and making the prediction
            if prediction and not await self._ticket_repository.ticket_is_resolved(ticket_id):
                await self._change_detail_work_queue(ticket_id, detail_id, serial_number, prediction)

    async def _change_detail_work_queue(self, ticket_id, detail_id, serial_number, queue_name):
        # If production or development do things here
        message = f'Prediction {queue_name} would have been applied to ticket {ticket_id} with serial {serial_number}'
        self._logger.info(f'{message}')
        slack_message = {'request_id': uuid(),
                         'message': "##ST-TNBA##" + message}
        await self._event_bus.rpc_request("notification.slack.request", slack_message, timeout=30)
