import json
import re

from datetime import datetime
from datetime import timedelta
from typing import NoReturn

from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from pytz import timezone
from shortuuid import uuid

from igz.packages.repositories.edge_repository import EdgeIdentifier


class ServiceOutageDetector:
    __client_id_regex = re.compile(r'^.*\|(?P<client_id>\d+)\|$')

    def __init__(self, event_bus, logger, scheduler, quarantine_edge_repository, reporting_edge_repository, config,
                 email_template_renderer, outage_utils):
        self._event_bus = event_bus
        self._logger = logger
        self._scheduler = scheduler
        self._reporting_edge_repository = reporting_edge_repository
        self._quarantine_edge_repository = quarantine_edge_repository
        self._config = config
        self._email_template_renderer = email_template_renderer
        self._outage_utils = outage_utils

    async def report_persisted_edges(self):
        self._logger.info('Reporting persisted edges prior to start scheduling jobs...')

        await self.start_service_outage_reporter_job(exec_on_start=True)

    async def load_persisted_quarantine(self):
        self._logger.info('Processing quarantine prior to start scheduling jobs...')

        quarantine_edges = self._quarantine_edge_repository.get_all_edges()
        for edge_identifier, edge_data in quarantine_edges.items():
            edge_full_id = edge_identifier._asdict()
            detection_timestamp = edge_data['addition_timestamp']

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
            self._logger.info(f'Skipping start of Service Outage Monitoring job. Reason: {conflict}')

    async def _outage_monitoring_process(self):
        edges_to_monitor = self._get_edges_for_monitoring()

        for edge_full_id in edges_to_monitor:
            edge_identifier = EdgeIdentifier(**edge_full_id)

            self._logger.info(f'[outage-monitoring] Checking status of {edge_identifier}.')
            edge_status = await self._get_edge_status_by_id(edge_full_id)
            self._logger.info(f'[outage-monitoring] Got status for edge: {edge_identifier}.')

            self._logger.info(f'[outage-monitoring] Getting management status for {edge_identifier}.')
            enterprise_name = edge_status['enterprise_name']
            bruin_client_id = self._extract_client_id(enterprise_name)
            serial_number = edge_status['edges']['serialNumber']
            management_request = {
                "request_id": uuid(),
                "filters": {
                    "client_id": bruin_client_id,
                    "status": "A",
                    "service_number": serial_number
                }}
            management_status = await self._event_bus.rpc_request("bruin.inventory.management.status",
                                                                  management_request, timeout=30)

            if not management_status["management_status"]:
                self._logger.error(f'Could not retrieve management status for {serial_number}')
                self._logger.error(f'Full message: {json.dumps(management_status, indent=2, default=str)}')
                self._logger.error(f'Considering it as inactive')
                continue

            self._logger.info(f'Got management status {management_status} for {serial_number}')
            if management_status["management_status"] \
                    not in "Pending, Active – Gold Monitoring, Active – Platinum Monitoring":
                self._logger.info(f'Management status is not active for {serial_number}. Skipping process')
                continue
            self._logger.info(f'Management status for {serial_number} seems active. Monitoring..')
            if not await self._is_management_status_active(edge_status):
                self._logger.info(
                    f'Management status is not active for {edge_status["edges"]["serialNumber"]}. Skipping process')
                return
            self._logger.info(
                f'Management status for {edge_status["edges"]["serialNumber"]} seems active. Monitoring..')

            outage_happened = self._outage_utils.is_there_an_outage(edge_status)
            if outage_happened:
                self._logger.info(
                    f'[outage-monitoring] Outage detected for {edge_identifier}. '
                    'Scheduling edge to re-check it in a few moments.'
                )

                try:
                    tz = timezone(self._config.MONITOR_CONFIG['timezone'])
                    current_datetime = datetime.now(tz)
                    run_date = current_datetime + timedelta(
                        seconds=self._config.MONITOR_CONFIG['jobs_intervals']['quarantine'])
                    self._scheduler.add_job(self._recheck_edge_for_ticket_creation, 'date',
                                            run_date=run_date,
                                            replace_existing=False,
                                            misfire_grace_time=9999,
                                            id=f'_ticket_creation_recheck_{json.dumps(edge_full_id)}',
                                            kwargs={'edge_full_id': edge_full_id})
                    self._logger.info(f'[outage-monitoring] {edge_identifier} successfully scheduled for re-check.')
                except ConflictingIdError:
                    self._logger.info(f'There is a recheck job scheduled for {edge_identifier} already. No new job '
                                      'is going to be scheduled.')
            else:
                self._logger.info(f'[outage-monitoring] {edge_identifier} is in healthy state. Skipping...')

    def _get_edges_for_monitoring(self):
        return list(self._config.MONITORING_EDGES.values())

    async def _recheck_edge_for_ticket_creation(self, edge_full_id):
        edge_identifier = EdgeIdentifier(**edge_full_id)

        self._logger.info(
            f"[outage-recheck] Checking status of {edge_identifier} to ensure it's still in outage state...")
        edge_status = await self._get_edge_status_by_id(edge_full_id)
        self._logger.info(f'[outage-recheck] Got status for edge {edge_identifier}.')

        is_outage = self._outage_utils.is_there_an_outage(edge_status)
        if is_outage:
            self._logger.info(f'[outage-recheck] Edge {edge_identifier} is still in outage state.')

            working_environment = self._config.MONITOR_CONFIG['environment']
            if working_environment == 'production':
                open_outage_ticket = await self._get_outage_ticket_for_edge(edge_status, ticket_statuses=None)
                open_outage_ticket_details = open_outage_ticket['ticket_details']
                open_ticket_exists = open_outage_ticket_details is not None

                # CAVEAT: This check should be performed by Bruin on their side. In the meanwhile...
                if open_ticket_exists:
                    self._logger.info(
                        f'[outage-recheck] Faulty edge {edge_identifier} already has an outage ticket with '
                        f'ID = {open_outage_ticket_details["ticketID"]}. Skipping ticket creation for this edge...')
                else:
                    resolved_outage_ticket = await self._get_outage_ticket_for_edge(
                        edge_status, ticket_statuses=['Resolved']
                    )
                    resolved_outage_ticket_details = resolved_outage_ticket['ticket_details']
                    resolved_ticket_exists = resolved_outage_ticket_details is not None

                    if resolved_ticket_exists:
                        self._logger.info(
                            f'[outage-recheck] Faulty edge {edge_identifier} already has an outage ticket with '
                            f'ID = {resolved_outage_ticket_details["ticketID"]}. Re-opening...')
                        await self._reopen_outage_ticket(
                            resolved_outage_ticket_details["ticketID"],
                            resolved_outage_ticket_details["ticketDetails"][0]["detailID"],
                            edge_status)
                    else:
                        self._logger.info(
                            f'[outage-recheck] Starting outage ticket creation for faulty edge {edge_identifier}.')
                        await self._create_outage_ticket(edge_full_id, edge_status)
            else:
                self._logger.info(
                    f'[outage-recheck] Not starting outage ticket creation for faulty edge {edge_identifier} because '
                    f'the current working environment is {working_environment.upper()}.'
                )
        else:
            self._logger.info(
                f'[outage-recheck] {edge_identifier} seems to be healthy again! No ticket will be created.')

    async def _create_outage_ticket(self, edge_full_id, edge_status):
        edge_identifier = EdgeIdentifier(**edge_full_id)

        ticket_data = self._generate_outage_ticket(edge_status)

        self._logger.info(f'[outage-ticket-creation] Creating outage ticket for edge {edge_identifier}...')
        ticket_creation_response = await self._event_bus.rpc_request(
            "bruin.ticket.creation.request", {'request_id': uuid(), **ticket_data}, timeout=30
        )

        ticket_id_data = ticket_creation_response['ticketIds']
        if ticket_id_data is not None:
            ticket_id = ticket_id_data['ticketIds'][0]
            self._logger.info(
                f'[outage-ticket-creation] Outage ticket (ID = {ticket_id}) created successfully '
                f'for faulty edge {edge_identifier}')

            enterprise_name = edge_status['enterprise_name']
            bruin_client_id = self._extract_client_id(enterprise_name)
            slack_message = {
                'request_id': uuid(),
                'message': f'Outage ticket created for faulty edge {edge_identifier}. Ticket '
                           f'details at https://app.bruin.com/helpdesk?clientId={bruin_client_id}&ticketId={ticket_id}.'
            }
            await self._event_bus.rpc_request("notification.slack.request", slack_message, timeout=10)
        else:
            self._logger.error(
                f'[outage-ticket-creation] Outage ticket creation failed for edge {edge_identifier}.'
            )

    async def _reopen_outage_ticket(self, ticket_id, detail_id, edge_status):
        self._logger.info(f'[outage-ticket-reopening] Reopening outage ticket {ticket_id}...')
        ticket_reopening_msg = {'request_id': uuid(), 'ticket_id': ticket_id, 'detail_id': detail_id}
        ticket_reopening_response = await self._event_bus.rpc_request(
            "bruin.ticket.status.open", ticket_reopening_msg, timeout=30
        )

        if ticket_reopening_response['status'] == 200:
            self._logger.info(
                f'[outage-ticket-reopening] Outage ticket {ticket_id} reopening succeeded.'
            )
            enterprise_name = edge_status['enterprise_name']
            bruin_client_id = self._extract_client_id(enterprise_name)
            slack_message = {
                'request_id': uuid(),
                'message': f'Outage ticket {ticket_id} reopened. Ticket details at '
                           f'https://app.bruin.com/helpdesk?clientId={bruin_client_id}&ticketId={ticket_id}.'
            }
            await self._event_bus.rpc_request("notification.slack.request", slack_message, timeout=10)
            await self._post_note_in_outage_ticket(ticket_id, edge_status)
        else:
            self._logger.error(
                f'[outage-ticket-creation] Outage ticket {ticket_id} reopening failed.'
            )

    async def _post_note_in_outage_ticket(self, ticket_id, edge_status):
        ticket_note_timestamp = datetime.now(timezone(self._config.MONITOR_CONFIG['timezone']))

        outage_causes = self._get_outage_causes(edge_status)
        ticket_note_outage_causes = 'Outage causes:'
        if outage_causes is not None:
            edge_state = outage_causes.get('edge')
            if edge_state is not None:
                ticket_note_outage_causes += f' Edge was {edge_state}.'

            links_states = outage_causes.get('links')
            if links_states is not None:
                for interface, state in links_states.items():
                    ticket_note_outage_causes += f' Link {interface} was {state}.'
        else:
            ticket_note_outage_causes += ' Could not determine causes.'

        ticket_note = (
            f'#*Automation Engine*#\n'
            f'Re-opening ticket.\n'
            f'{ticket_note_outage_causes}\n'
            f'TimeStamp: {str(ticket_note_timestamp)}'
        )

        ticket_append_note_msg = {'request_id': uuid(), 'ticket_id': ticket_id, 'note': ticket_note}

        self._logger.info(f'[outage-ticket-reopening] Posting reopening note in ticket {ticket_id}...')
        await self._event_bus.rpc_request("bruin.ticket.note.append.request", ticket_append_note_msg, timeout=15)

    def _generate_outage_ticket(self, edge_status):
        serial_number = edge_status['edges']['serialNumber']
        enterprise_name = edge_status['enterprise_name']
        bruin_client_id = self._extract_client_id(enterprise_name)

        return {
            "clientId": bruin_client_id,
            "category": "VOO",
            "services": [
                {"serviceNumber": serial_number}
            ],
            "contacts": self._config.OUTAGE_CONTACTS[f'{serial_number}'],
        }

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
            if not await self._is_management_status_active(edge_status):
                self._logger.info("Managemnt status is not active , skipping monitoring...")
                return
            if self._outage_utils.is_there_an_outage(edge_status):
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
        edge_value = {'edge_status': edge_status}

        edge_ttl = self._config.MONITOR_CONFIG['quarantine_key_ttl']
        self._quarantine_edge_repository.add_edge(
            edge_full_id, edge_value,
            update_existing=False,  # Preserves the timestamp of the original detection if the edge is in quarantine
            time_to_live=edge_ttl)

        self._logger.info(f'Edge {edge_identifier} sent to quarantine')

    def _get_outage_causes(self, edge_status):
        outage_causes = {}

        edge_state = edge_status["edges"]["edgeState"]
        if self._outage_utils.is_faulty_edge(edge_state):
            outage_causes['edge'] = edge_state

        for link in edge_status['links']:
            link_data = link['link']
            link_state = link_data['state']

            if self._outage_utils.is_faulty_link(link_state):
                outage_links_states = outage_causes.setdefault('links', {})
                outage_links_states[link_data['interface']] = link_state

        return outage_causes or None

    def _generate_edge_url(self, edge_full_id):
        url = 'https://{host}/#!/operator/customer/{enterprise_id}/monitor/edge/{edge_id}/'
        return url.format(**edge_full_id)

    def _unmarshall_edge_to_report(self, edge_identifier: EdgeIdentifier, edge_value: dict):
        edge_status = edge_value['edge_status']
        edge_status_device_info = edge_status['edges']

        edge_name = edge_status_device_info['name']
        last_contact = edge_status_device_info['lastContact']
        edge_serial = edge_status_device_info['serialNumber']
        enterprise_name = edge_status['enterprise_name']

        edge_full_id = edge_identifier._asdict()
        edge_url = self._generate_edge_url(edge_full_id)

        outage_detection_timestamp = edge_value['detection_timestamp']
        tz = timezone(self._config.MONITOR_CONFIG['timezone'])
        outage_detection_datetime = datetime.fromtimestamp(outage_detection_timestamp, tz=tz)

        outage_causes = []
        edge_state = edge_value['outage_causes'].get('edge')
        if edge_state is not None:
            outage_causes.append(f"Edge was {edge_state}")

        links_states: dict = edge_value['outage_causes'].get('links', {})
        for interface, state in links_states.items():
            outage_causes.append(f"Link {interface} was {state}")

        return {
            'detection_time': outage_detection_datetime,
            'edge_name': edge_name,
            'last_contact': last_contact,
            'serial_number': edge_serial,
            'enterprise': enterprise_name,
            'edge_url': edge_url,
            'outage_causes': outage_causes,
        }

    async def _service_outage_reporter_process(self):
        # self._logger.info(f'Refreshing reporting queue to update faulty edges and remove recovered ones...')
        # await self._refresh_reporting_queue()

        edges_to_report = self._reporting_edge_repository.get_all_edges()
        if not edges_to_report:
            self._logger.info(f'Nothing to report!')
            return

        self._attach_outage_causes_to_edges(edges_to_report)

        edges_for_email_template = [
            self._unmarshall_edge_to_report(edge_identifier, edge_value)
            for edge_identifier, edge_value in edges_to_report.items()
        ]
        self._logger.info(f'Reporting {len(edges_for_email_template)} outages without ticket...')

        # TODO: Move these fields to a proper place as they will always be the same in every outage report
        fields = ["Date of detection", "Company", "Edge name", "Last contact", "Serial Number", "Edge URL",
                  "Outage causes"]
        fields_edge = ["detection_time", "enterprise", "edge_name", "last_contact", "serial_number", "edge_url",
                       "outage_causes"]
        email_report = self._email_template_renderer.compose_email_object(edges_for_email_template, fields=fields,
                                                                          fields_edge=fields_edge)
        await self._event_bus.rpc_request("notification.email.request", email_report, timeout=10)

        self._logger.info(f'Outage report sent via e-mail! Clearing up the reporting queue...')
        self._reporting_edge_repository.remove_all_stored_elements()

    async def _refresh_reporting_queue(self) -> NoReturn:
        edges_to_report = self._reporting_edge_repository.get_all_edges()

        for edge_identifier, edge_value in edges_to_report.items():
            edge_full_id = edge_identifier._asdict()
            edge_new_status = await self._get_edge_status_by_id(edge_full_id)

            try:
                is_reportable_edge = await self._is_reportable_edge(edge_new_status)
            except ValueError:
                self._logger.error(
                    f'An error ocurred while trying to look up an outage ticket for edge {edge_identifier}. '
                    'It will not be removed from the reporting queue because its current status is unknown.'
                )
            else:
                if is_reportable_edge:
                    edge_new_value = {**edge_value, **{'edge_status': edge_new_status}}
                    self._reporting_edge_repository.add_edge(
                        edge_full_id, edge_new_value, update_existing=True, time_to_live=None
                    )
                else:
                    self._reporting_edge_repository.remove_edge(edge_full_id)

    def _attach_outage_causes_to_edges(self, edges_to_report) -> NoReturn:
        for edge_identifier, edge_value in edges_to_report.items():
            edge_status = edge_value['edge_status']
            edges_to_report[edge_identifier]['outage_causes'] = self._get_outage_causes(edge_status)

    async def _get_all_edges(self):
        edge_list_request_dict = {
            'request_id': uuid(),
            'filter': []
        }
        edge_list_response = await self._event_bus.rpc_request(
            'edge.list.request', edge_list_request_dict, timeout=600,
        )

        return edge_list_response['edges']

    async def _process_edge_from_quarantine(self, edge_full_id):
        edge_identifier = EdgeIdentifier(**edge_full_id)
        edge_status = await self._get_edge_status_by_id(edge_full_id)

        try:
            is_reportable_edge = await self._is_reportable_edge(edge_status)
        except ValueError:
            self._logger.error(
                f'An error ocurred while trying to look up an outage ticket for edge {edge_identifier}. '
                'Skipping edge for now...'
            )
        else:
            if is_reportable_edge:
                self._add_edge_to_reporting(edge_full_id, edge_status)
            else:
                self._logger.info(
                    f'Edge {edge_identifier} may be healthy again or there may be an outage ticket '
                    'created for it already (or both). This edge will not be reported for now.'
                )
                self._quarantine_edge_repository.remove_edge(edge_full_id)

    async def _is_reportable_edge(self, edge_status):
        outage_happened = self._outage_utils.is_there_an_outage(edge_status)
        if not outage_happened:
            return False

        outage_ticket = await self._get_outage_ticket_for_edge(edge_status)
        if outage_ticket is None:
            raise ValueError

        edge_has_ticket = outage_ticket['ticket_details'] is not None
        if edge_has_ticket:
            return False

        return True

    async def _get_edge_status_by_id(self, edge_full_id):
        edge_status_request_dict = {
            'request_id': uuid(),
            'edge': edge_full_id,
        }
        edge_status_response = await self._event_bus.rpc_request(
            'edge.status.request', edge_status_request_dict, timeout=120,
        )

        return edge_status_response['edge_info']

    async def _get_outage_ticket_for_edge(self, edge_status: dict, ticket_statuses=None):
        edge_serial = edge_status['edges']['serialNumber']
        enterprise_name = edge_status['enterprise_name']
        client_id = self._extract_client_id(enterprise_name)

        outage_ticket_request = {'request_id': uuid(), 'edge_serial': edge_serial, 'client_id': client_id}

        if ticket_statuses is not None:
            outage_ticket_request['ticket_statuses'] = ticket_statuses

        outage_ticket = await self._event_bus.rpc_request(
            'bruin.ticket.outage.details.by_edge_serial.request', outage_ticket_request, timeout=180,
        )
        return outage_ticket

    def _extract_client_id(self, enterprise_name):
        client_id_match = self.__client_id_regex.match(enterprise_name)

        if client_id_match:
            client_id = client_id_match.group('client_id')
            return int(client_id)
        else:
            return 9994

    def _add_edge_to_reporting(self, edge_full_id, edge_status):
        edge_identifier = EdgeIdentifier(**edge_full_id)
        edge_from_quarantine = self._quarantine_edge_repository.get_edge(edge_full_id)

        if edge_from_quarantine is None:
            tz = timezone(self._config.MONITOR_CONFIG['timezone'])
            current_timestamp = datetime.timestamp(datetime.now(tz))
            outage_detection_timestamp = current_timestamp - self._config.MONITOR_CONFIG['jobs_intervals']['quarantine']
        else:
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

    async def _is_management_status_active(self, edge_status):
        enterprise_name = edge_status['enterprise_name']
        bruin_client_id = self._extract_client_id(enterprise_name)
        serial_number = edge_status['edges']['serialNumber']
        management_request = {
            "request_id": uuid(),
            "filters": {
                "client_id": bruin_client_id,
                "status": "A",
                "service_number": serial_number
            }
        }
        management_status = await self._event_bus.rpc_request("bruin.inventory.management.status",
                                                              management_request, timeout=30)
        print(management_status)
        self._logger.info(f'Got management status {management_status} for {serial_number}')
        if management_status["management_status"] in "Pending, Active – Silver Monitoring, " \
                                                     "Active – Gold Monitoring, Active – Platinum Monitoring":
            return True
        return False
