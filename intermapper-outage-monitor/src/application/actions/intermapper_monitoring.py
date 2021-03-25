import json
import time
from datetime import datetime

from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from pytz import timezone


class InterMapperMonitor:
    def __init__(self, event_bus, logger, scheduler, config, notifications_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._scheduler = scheduler
        self._config = config
        self._notifications_repository = notifications_repository

    async def start_intermapper_outage_monitoring(self, exec_on_start):
        self._logger.info('Scheduling InterMapper Monitor job...')
        next_run_time = undefined

        if exec_on_start:
            tz = timezone(self._config.INTERMAPPER_CONFIG['timezone'])
            next_run_time = datetime.now(tz)
            self._logger.info('InterMapper Monitor job is going to be executed immediately')

        try:
            self._scheduler.add_job(self._intermapper_monitoring_process, 'interval',
                                    seconds=self._config.INTERMAPPER_CONFIG['monitoring_interval'],
                                    next_run_time=next_run_time, replace_existing=False,
                                    id='_intermapper_monitor_process')
        except ConflictingIdError as conflict:
            self._logger.info(f'Skipping start of InterMapper Monitoring job. Reason: {conflict}')

    async def _intermapper_monitoring_process(self):
        self._logger.info(f'Processing all unread email from {self._config.INTERMAPPER_CONFIG["inbox_email"]}')
        start = time.time()
        unread_emails_response = await self._notifications_repository.get_unread_emails()
        unread_emails_body = unread_emails_response['body']
        unread_emails_status = unread_emails_response['status']
        if unread_emails_status not in range(200, 300):
            return
        for email in unread_emails_body:
            message = email['message']
            body = email['body']
            msg_uid = email['msg_uid']
            if message is None or msg_uid == -1:
                self._logger.error('Invalid message')
                return
            self._logger.info(f'Processing email: {msg_uid}')
            mark_email_as_read_response = await self._notifications_repository.mark_email_as_read(msg_uid)
            mark_email_as_read_status = mark_email_as_read_response['status']
            if mark_email_as_read_status not in range(200, 300):
                self._logger.error('Could not mark email as read')
                return
            self._logger.info(f"'Parsing through email: {msg_uid}'s body to create a dict'")

            parsed_email_dict = self._parse_email_body(body)
            slack_message = f'Parsed email {msg_uid} into a dictionary:\n{json.dumps(parsed_email_dict, indent=2)}'
            await self._notifications_repository.send_slack_message(slack_message)

        stop = time.time()
        self._logger.info(f'Finished processing all unread email from {self._config.INTERMAPPER_CONFIG["inbox_email"]}'
                          f'Elapsed time:{round((stop - start) / 60, 2)} minutes')

    def _parse_email_body(self, body):
        parsed_email_dict = {}
        parsed_email_dict['event'] = self._find_field_in_body(body, 'Event')
        parsed_email_dict['name'] = self._find_field_in_body(body, 'Name')
        parsed_email_dict['document'] = self._find_field_in_body(body, 'Document')
        parsed_email_dict['address'] = self._find_field_in_body(body, 'Address')
        parsed_email_dict['probe_type'] = self._find_field_in_body(body, 'Probe Type')
        parsed_email_dict['condition'] = self._find_field_in_body(body, 'Condition')
        parsed_email_dict['last_reported_down'] = self._find_field_in_body(body, 'Time since last reported down')
        parsed_email_dict['up_time'] = self._find_field_in_body(body, "Device's up time")
        return parsed_email_dict

    def _find_field_in_body(self, email_body, field_name):
        email_body_lines = email_body.splitlines()
        field = None
        for line in email_body_lines:
            if line and len(line) > 0 and field_name in line:
                field = ''.join(ch for ch in line)
                break
        if field is None or field.strip() == '':
            return None
        return field.strip().replace(f'{field_name}: ', '')
