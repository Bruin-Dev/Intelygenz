import time
from datetime import datetime

from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from pytz import timezone


class InterMapperMonitor:
    def __init__(self, event_bus, logger, scheduler, config, notifications_repository, bruin_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._scheduler = scheduler
        self._config = config
        self._notifications_repository = notifications_repository
        self._bruin_repository = bruin_repository

    async def start_intermapper_outage_monitoring(self, exec_on_start=False):
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
                continue
            self._logger.info(f'Processing email: {msg_uid}')
            mark_email_as_read_response = await self._notifications_repository.mark_email_as_read(msg_uid)
            mark_email_as_read_status = mark_email_as_read_response['status']
            if mark_email_as_read_status not in range(200, 300):
                self._logger.error('Could not mark email as read')
                continue
            self._logger.info(f"'Parsing through email: {msg_uid}'s body to create a dict'")

            parsed_email_dict = self._parse_email_body(body)
            if parsed_email_dict['event'] not in self._config.INTERMAPPER_CONFIG['intermapper_events']:
                self._logger.info(f'Event from intermapper was {parsed_email_dict["event"]} there is no need to create'
                                  f'a new ticket. Skipping ...')
                continue
            self._logger.info('Grabbing the asset_id from the Intermapper email')
            asset_id = self._extract_value_from_field('(', ')', parsed_email_dict['name'])
            if asset_id is None or asset_id == 'SD-WAN':
                continue
            self._logger.info('Grabbing the client_id from the Intermapper email')
            client_id = self._extract_value_from_field('|', '|', parsed_email_dict['document'])
            self._logger.info(f'Got client_id {client_id} from the Intermapper email')
            if client_id is None:
                continue
            circuit_id_response = await self._bruin_repository.get_circuit_id(asset_id, client_id)
            circuit_id_status = circuit_id_response['status']
            if circuit_id_status not in range(200, 300) or circuit_id_status == 204:
                continue
            circuit_id_body = circuit_id_response['body']
            circuit_id = circuit_id_body['wtn']
            self._logger.info(f'Got circuit_id from bruin: {circuit_id}')

            self._logger.info(f'Attempting outage ticket creation for client_id {client_id}, '
                              f'and circuit_id {circuit_id}')
            outage_ticket_response = await self._bruin_repository.create_outage_ticket(client_id, circuit_id)
            outage_ticket_status = outage_ticket_response['status']
            if outage_ticket_status not in range(200, 300):
                continue
            outage_ticket_body = outage_ticket_response['body']

            self._logger.info(f'Successfully created outage ticket with ticket_id {outage_ticket_body}')
            slack_message = (
                f'Outage ticket created through Intermapper emails for circuit_id {circuit_id}. Ticket '
                f'details at https://app.bruin.com/t/{outage_ticket_body}.'
            )
            await self._notifications_repository.send_slack_message(slack_message)
            self._logger.info(f'Appending Intermapper note to ticket id {outage_ticket_body}')
            await self._bruin_repository.append_intermapper_note(outage_ticket_body, body)

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

    def _extract_value_from_field(self, starting_char, ending_char, field):
        extracted_value = None
        if all(char in field for char in (starting_char, ending_char)):
            if starting_char == ending_char:
                extracted_value = field.split(starting_char)[1]
            else:
                extracted_value = field.split(starting_char)[1].split(ending_char)[0]
        return extracted_value
