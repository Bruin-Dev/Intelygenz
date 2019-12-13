import json
import re

from datetime import datetime
from datetime import timedelta

from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from pytz import timezone
from shortuuid import uuid

from application.repositories.edge_repository import EdgeIdentifier


class ServiceOutageDetector:
    __client_id_regex = re.compile(r'^.*\|(?P<client_id>\d+)\|$')

    def __init__(self, event_bus, logger, scheduler, quarantine_edge_repository, reporting_edge_repository, config,
                 email_template_renderer):
        self._event_bus = event_bus
        self._logger = logger
        self._scheduler = scheduler
        self._reporting_edge_repository = reporting_edge_repository
        self._quarantine_edge_repository = quarantine_edge_repository
        self._config = config
        self._email_template_renderer = email_template_renderer

    async def load_persisted_quarantine(self):
        quarantine_edges = self._quarantine_edge_repository.get_all_edges()
        for edge_identifier, edge_data in quarantine_edges.items():
            edge_full_id = edge_identifier._asdict()
            edge_dict = json.loads(edge_data)
            detection_timestamp = edge_dict['addition_timestamp']

            job_run_date = datetime.fromtimestamp(detection_timestamp) + timedelta(
                seconds=self._config.MONITOR_CONFIG['jobs_intervals']['quarantine'])
            await self._start_quarantine_job(edge_full_id, run_date=job_run_date)

    async def start_service_outage_detector_job(self, exec_on_start=False):
        self._logger.info('Scheduling Service Outage Detector job...')
        next_run_time = undefined

        if exec_on_start:
            tz = timezone(self._config.MONITOR_CONFIG['timezone'])
            next_run_time = datetime.now(tz)
            self._logger.info('Service Outage Detector job is going to be executed immediately')

        try:
            self._scheduler.add_job(self._service_outage_detector_process, 'interval',
                                    seconds=self._config.MONITOR_CONFIG['jobs_intervals']['outage_detector'],
                                    next_run_time=next_run_time, replace_existing=False,
                                    id='_service_outage_detector_process')
        except ConflictingIdError as conflict:
            self._logger.info(f'Skipping start of Service Outage Detector job. Reason: {conflict}')

    async def start_service_outage_monitoring(self, exec_on_start):
        self._logger.info('Scheduling Service Outage Monitor job...')
        next_run_time = undefined

        if exec_on_start:
            tz = timezone(self._config.MONITOR_CONFIG['timezone'])
            next_run_time = datetime.now(tz)
            self._logger.info('Service Outage Monitor job is going to be executed immediately')

        try:
            self._scheduler.add_job(self._outage_monitoring_process, 'interval',
                                    seconds=self._config.MONITOR_CONFIG['jobs_intervals']['outage_monitor'],
                                    next_run_time=next_run_time, replace_existing=False,
                                    id='_service_outage_monitor_process')
        except ConflictingIdError as conflict:
            self._logger.info(f'Skipping start of Service Outage Detector job. Reason: {conflict}')

    async def _outage_monitoring_process(self):
        edge_id = {
            "host": "metvco02.mettel.net",
            "enterprise_id": 1,
            "edge_id": 4784
        }
        self._logger.info(f'Checking status of {edge_id}.')
        edge_status_request_dict = {
            'request_id': uuid(),
            'edge': edge_id,
        }
        edge_status_response = await self._event_bus.rpc_request(
            'edge.status.request',
            json.dumps(edge_status_request_dict),
            timeout=45,
        )
        self._logger.info(f'Got status for edge: {edge_id}.')
        edge_info = edge_status_response['edge_info']

        is_outage = self._is_there_an_outage(edge_info)

        if is_outage:
            self._logger.info(f'Outage detected for {edge_id}. Scheduling edge for quarantine')
            try:
                self._scheduler.add_job(self._ticket_creation_quarantine, 'interval',
                                        seconds=self._config.MONITOR_CONFIG['jobs_intervals']['quarantine'],
                                        replace_existing=False,
                                        id='_ticket_creation_quarantine',
                                        kwargs={'edge_id': edge_id})
                self._logger.info(f'{edge_id} scheduled for quarantine!')
            except ConflictingIdError as conflict:
                self._logger.info(f'Not rescheduling quarantine for ticket creation. Reason: {conflict}')

    async def _ticket_creation_quarantine(self, edge_id):
        edge_status_request_dict = {
            'request_id': uuid(),
            'edge': edge_id,
        }
        self._logger.info(f'Quarantine: Checking status of {edge_id}.')

        edge_status_response = await self._event_bus.rpc_request(
            'edge.status.request',
            json.dumps(edge_status_request_dict),
            timeout=45,
        )
        self._logger.info(f'Quarantine: Got status for edge {edge_id}.')
        edge_info = edge_status_response['edge_info']

        is_outage = self._is_there_an_outage(edge_info)
        if is_outage:
            self._logger.info(f'Quarantine: Edge {edge_id} is still in outage state. Creating ticket.')
            await self._create_outage_ticket(edge_id)

    async def _create_outage_ticket(self, edge_id):
        ticket_details = {
            "request_id": uuid(),
            "clientId": 9994,
            "category": "VOO",
            "services": [
                {
                    "serviceNumber": "VC05400002265"
                }
            ],
            "contacts": [
                {
                    "email": "ndimuro@mettel.net",
                    "phone": "732-837-9570",
                    "name": "Nicholas Di Muro",
                    "type": "site"
                },
                {
                    "email": "ndimuro@mettel.net",
                    "phone": "732-837-9570",
                    "name": "Nicholas Di Muro",
                    "type": "ticket"
                }
            ]
        }
        ticket_id = await self._event_bus.rpc_request("bruin.ticket.creation.request",
                                                      json.dumps(ticket_details), timeout=30)
        self._logger.info(
            f'Ticket creation: Edge {edge_id} is still in outage state. Ticket created with id {ticket_id}')

        slack_message = {'request_id': uuid(),
                         'message': f'Outage ticket created: https://app.bruin.com'
                                    f'/helpdesk?clientId=9994&ticketId={ticket_id["ticketIds"]["ticketIds"][0]}'}
        await self._event_bus.rpc_request("notification.slack.request", json.dumps(slack_message), timeout=10)
        # Change hardcoded URL generation in service-outage-triage
        # Check and print errors from Bruin (Like, shit already exists)
        # Check the environment and avoid ticket creation when not in production environment

    async def start_service_outage_reporter_job(self, exec_on_start=False):
        self._logger.info('Scheduling Service Outage Reporter job...')
        next_run_time = undefined

        if exec_on_start:
            tz = timezone(self._config.MONITOR_CONFIG['timezone'])
            next_run_time = datetime.now(tz)
            self._logger.info('Service Outage Reporter job is going to be executed immediately')

        self._scheduler.add_job(self._service_outage_reporter_process, 'interval',
                                seconds=self._config.MONITOR_CONFIG['jobs_intervals']['outage_reporter'],
                                next_run_time=next_run_time, replace_existing=True,
                                id='_service_outage_reporter_process')

    async def _service_outage_detector_process(self):
        self._logger.info(
            'Triggering new Service Outage Detector job. Current datetime is '
            f'{datetime.now(timezone(self._config.MONITOR_CONFIG["timezone"]))}'
        )

        edge_list = await self._get_all_edges()
        for edge_full_id in edge_list:
            edge_status = await self._get_edge_status_by_id(edge_full_id)

            if self._is_there_an_outage(edge_status):
                await self._start_quarantine_job(edge_full_id)
                self._add_edge_to_quarantine(edge_full_id, edge_status)

    async def _start_quarantine_job(self, edge_full_id, run_date: datetime = None):
        edge_identifier = EdgeIdentifier(**edge_full_id)

        if run_date is None:
            tz = timezone(self._config.MONITOR_CONFIG['timezone'])
            current_datetime = datetime.now(tz)
            run_date = current_datetime + timedelta(seconds=self._config.MONITOR_CONFIG['jobs_intervals']['quarantine'])

        self._logger.info(f'Scheduling Quarantine job for edge "{edge_identifier}"...')

        try:
            self._scheduler.add_job(self._process_edge_from_quarantine, 'date',
                                    run_date=run_date, replace_existing=False, misfire_grace_time=9999,
                                    id=f'_quarantine_{json.dumps(edge_full_id)}',
                                    kwargs={'edge_full_id': edge_full_id})
            self._logger.info(f'Quarantine job for edge "{edge_identifier}" will be launched at {run_date}.')
        except ConflictingIdError as conflict:
            self._logger.info(f'Quarantine job for edge "{edge_identifier}" will not be scheduled. Reason: {conflict}')

    def _add_edge_to_quarantine(self, edge_full_id, edge_status):
        edge_identifier = EdgeIdentifier(**edge_full_id)

        edge_ttl = self._config.MONITOR_CONFIG['quarantine_key_ttl']
        self._quarantine_edge_repository.add_edge(
            edge_full_id, edge_status,
            update_existing=False,  # Allows to preserve the timestamp of the first detection if the edge is already
            # in quarantine
            time_to_live=edge_ttl)

        self._logger.info(f'Edge {edge_identifier} sent to quarantine')

    def _is_there_an_outage(self, edge_status):
        # is_edge_offline = edge_status["edges"]["edgeState"] == 'OFFLINE'
        # is_any_link_disconnected = any(
        #     link_status['link']['state'] == 'DISCONNECTED'
        #     for link_status in edge_status['links']
        # )
        #
        # return is_edge_offline or is_any_link_disconnected
        return True

    def _generate_urls_from_edge(self, edge_data, host):
        edge_info = edge_data["edges"]
        edge_id = edge_info["id"]
        enterprise_id = edge_info["enterpriseId"]

        links = f'https://{host}/#!/operator/customer/{enterprise_id}/monitor/edge/{edge_id}/'

        return links

    def _unmarshall_edge_to_report(self, edge_json_string, host):
        edge_to_report = {
            "detection_time": None,
            "serial_number": None,
            "enterprise": None,
            "links": None
        }
        edge = json.loads(edge_json_string)
        edge_data = edge["edge_status"]["edge_status"]
        detection_timestamp = edge["edge_status"]["detection_timestamp"]
        tz = timezone(self._config.MONITOR_CONFIG['timezone'])
        edge_to_report["detection_time"] = datetime.fromtimestamp(detection_timestamp, tz=tz)
        edge_to_report["serial_number"] = edge_data["edges"]["serialNumber"]
        edge_to_report["enterprise"] = edge_data["enterprise_name"]
        edge_to_report["links"] = self._generate_urls_from_edge(edge_data, host)
        return edge_to_report

    async def _service_outage_reporter_process(self):
        edges_to_report = self._reporting_edge_repository.get_all_edges()
        sanitized_list = []
        for field, value in edges_to_report.items():
            host = str(field)
            host = host.split("__")[1].split(',')[0].replace('\'', '')
            edge_to_report = self._unmarshall_edge_to_report(value, host)
            sanitized_list.append(edge_to_report)

        if len(sanitized_list) > 0:
            self._logger.info(f'Reporting {len(sanitized_list)} outages without ticket...')
            fields = ["Date of detection", "Serial Number", "Company", "Edge URL"]
            fields_edge = ["detection_time", "serial_number", "enterprise", "links"]
            email_report = self._email_template_renderer.compose_email_object(sanitized_list, fields=fields,
                                                                              fields_edge=fields_edge)
            await self._event_bus.rpc_request("notification.email.request",
                                              json.dumps(email_report),
                                              timeout=10)
            self._reporting_edge_repository.remove_all_stored_elements()

        else:
            self._logger.info(f'Nothing to report!')

    async def _get_all_edges(self):
        edge_list_request_dict = {
            'request_id': uuid(),
            'filter': []
        }
        edge_list_response = await self._event_bus.rpc_request(
            'edge.list.request',
            json.dumps(edge_list_request_dict),
            timeout=600,
        )

        return edge_list_response['edges']

    async def _process_edge_from_quarantine(self, edge_full_id):
        edge_identifier = EdgeIdentifier(**edge_full_id)
        edge_status = await self._get_edge_status_by_id(edge_full_id)

        if self._is_there_an_outage(edge_status):
            outage_ticket = await self._get_outage_ticket_for_edge(edge_status)

            if outage_ticket:
                if outage_ticket['ticket_details'] is None:
                    self._add_edge_to_reporting(edge_full_id, edge_status)
                else:
                    self._logger.info(
                        f'Edge {edge_identifier} has an outage but there is already '
                        'an outage ticket created for it. This edge will not be reported.'
                    )
            else:
                self._logger.info(
                    f'An error ocurred while trying to look up an outage ticket for edge {edge_identifier}. '
                    'Skipping edge for now...'
                )

    async def _get_edge_status_by_id(self, edge_full_id):
        edge_status_request_dict = {
            'request_id': uuid(),
            'edge': edge_full_id,
        }
        edge_status_response = await self._event_bus.rpc_request(
            'edge.status.request',
            json.dumps(edge_status_request_dict),
            timeout=45,
        )

        return edge_status_response['edge_info']

    async def _get_outage_ticket_for_edge(self, edge_value: dict):
        edge_serial = edge_value['edges']['serialNumber']
        enterprise_name = edge_value['enterprise_name']
        client_id = self._extract_client_id(enterprise_name)

        # In case is a test edge, they don't have |BruinId| in the company name
        if client_id is None:
            # This will make the code believe there's already a ticket for it
            return {}

        outage_ticket_request = {'request_id': uuid(), 'edge_serial': edge_serial, 'client_id': client_id}
        outage_ticket = await self._event_bus.rpc_request(
            'bruin.ticket.outage.details.by_edge_serial.request',
            json.dumps(outage_ticket_request),
            timeout=60,
        )
        return outage_ticket

    def _extract_client_id(self, enterprise_name):
        client_id_match = self.__client_id_regex.match(enterprise_name)

        if client_id_match:
            client_id = client_id_match.group('client_id')
            return client_id
        else:
            return None

    def _add_edge_to_reporting(self, edge_full_id, edge_status):
        edge_identifier = EdgeIdentifier(**edge_full_id)
        edge_from_quarantine = self._quarantine_edge_repository.get_edge(edge_full_id)

        if edge_from_quarantine is None:
            tz = timezone(self._config.MONITOR_CONFIG['timezone'])
            current_timestamp = datetime.timestamp(datetime.now(tz))
            outage_detection_timestamp = current_timestamp - self._config.MONITOR_CONFIG['jobs_intervals']['quarantine']
        else:
            edge_from_quarantine = json.loads(edge_from_quarantine)
            outage_detection_timestamp = edge_from_quarantine['addition_timestamp']

        edge_status_for_reporting = {
            'edge_status': edge_status,
            'detection_timestamp': outage_detection_timestamp,
        }

        self._reporting_edge_repository.add_edge(
            edge_full_id,
            edge_status_for_reporting,
            time_to_live=None,  # The key must live until we explicitly clear up the reporting queue
        )
        self._quarantine_edge_repository.remove_edge(edge_full_id)

        self._logger.info(f'Edge {edge_identifier} moved from quarantine to the reporting queue.')
