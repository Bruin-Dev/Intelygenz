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


class ComparisonReport:
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
            edge_identifier = EdgeIdentifier(**edge_full_id)
            try:
                self._logger.info(f'[outage-report] Checking status of {edge_identifier}.')

                full_edge_status = await self._get_edge_status_by_id(edge_full_id)
                self._logger.info(f'[outage-report] Got status for edge: {edge_identifier}.')
                edge_status = {}
                if full_edge_status["status"] in range(200, 300):
                    edge_status = full_edge_status["body"]["edge_info"]
                    management_status = await self._get_management_status(edge_status)
                else:
                    management_status = {"status": 500, "body": None}

                if management_status["status"] not in range(200, 300):
                    self._logger.info(f"Management status is unknown for {edge_identifier}")
                    if management_status["status"] == 500:
                        message = (
                            f"[outage-report] Management status is unknown for {edge_identifier}. "
                            f"Cause: {management_status['body']}"
                        )
                        slack_message = {'request_id': uuid(),
                                         'message': message}
                        await self._event_bus.rpc_request("notification.slack.request", slack_message, timeout=30)
                    continue

                if not self._is_management_status_active(management_status["body"]):
                    self._logger.info(f"Management status is not active. {edge_identifier} won't be reported")
                    continue
                else:
                    self._logger.info(
                        f"Management status is active. Checking outage state for {edge_identifier}...")

                if self._outage_utils.is_there_an_outage(edge_status):
                    await self._start_quarantine_job(edge_full_id)
                    self._add_edge_to_quarantine(edge_full_id, edge_status)
            except Exception:
                self._logger.exception(f"Unexpected error occurred while running the detection process for edge "
                                       f"{edge_identifier}. Skipping...")

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

        client_id_exists = bool(self.__client_id_regex.match(enterprise_name))
        management_status = "A" if client_id_exists else "?"

        return {
            'detection_time': outage_detection_datetime,
            'edge_name': edge_name,
            'last_contact': last_contact,
            'serial_number': edge_serial,
            'enterprise': enterprise_name,
            'edge_url': edge_url,
            'outage_causes': outage_causes,
            'management_status': management_status,
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
                  "Outage causes", "Management status"]
        fields_edge = ["detection_time", "enterprise", "edge_name", "last_contact", "serial_number", "edge_url",
                       "outage_causes", "management_status"]
        email_report = self._email_template_renderer.compose_email_object(edges_for_email_template, fields=fields,
                                                                          fields_edge=fields_edge)
        await self._event_bus.rpc_request("notification.email.request", email_report, timeout=10)

        self._logger.info(f'Outage report sent via e-mail! Clearing up the reporting queue...')
        self._reporting_edge_repository.remove_all_stored_elements()

    async def _refresh_reporting_queue(self) -> NoReturn:
        edges_to_report = self._reporting_edge_repository.get_all_edges()

        for edge_identifier, edge_value in edges_to_report.items():
            edge_full_id = edge_identifier._asdict()

            try:
                full_edge_new_status = await self._get_edge_status_by_id(edge_full_id)
                edge_new_status = full_edge_new_status["body"].get("edge_info")
                try:
                    is_reportable_edge = await self._is_reportable_edge(edge_new_status)
                except ValueError as e:
                    self._logger.error(
                        f'An error ocurred while trying to look up an outage ticket for edge {edge_identifier}. '
                        f'It will not be removed from the reporting queue because its current status is unknown. '
                        f'Cause: {e}'
                    )
                    message = (
                        "[refresh-reporting-queue] An error ocurred while trying to look an outage ticket up "
                        f"for edge {edge_identifier}. It will not be removed from the reporting queue "
                        f"because its current status is unknown. Cause: {e}"
                    )
                    slack_message = {'request_id': uuid(),
                                     'message': message}
                    await self._event_bus.rpc_request("notification.slack.request", slack_message, timeout=30)
                else:
                    if is_reportable_edge:
                        edge_new_value = {**edge_value, **{'edge_status': edge_new_status}}
                        self._reporting_edge_repository.add_edge(
                            edge_full_id, edge_new_value, update_existing=True, time_to_live=None
                        )
                    else:
                        self._reporting_edge_repository.remove_edge(edge_full_id)
            except Exception:
                self._logger.exception(f"Unexpected error occurred while refreshing the reporting queue for edge "
                                       f"{edge_identifier}. Skipping...")

    def _attach_outage_causes_to_edges(self, edges_to_report) -> NoReturn:
        for edge_identifier, edge_value in edges_to_report.items():
            edge_status = edge_value['edge_status']
            edges_to_report[edge_identifier]['outage_causes'] = self._get_outage_causes(edge_status)

    async def _get_all_edges(self):
        edge_list_request_dict = {
            'request_id': uuid(),
            'body': {'filter': {}}
        }
        edge_list_response = await self._event_bus.rpc_request(
            'edge.list.request', edge_list_request_dict, timeout=600,
        )

        return edge_list_response['body']

    async def _process_edge_from_quarantine(self, edge_full_id):
        edge_identifier = EdgeIdentifier(**edge_full_id)
        full_edge_status = await self._get_edge_status_by_id(edge_full_id)
        edge_status = full_edge_status["body"].get("edge_info")
        try:
            is_reportable_edge = await self._is_reportable_edge(edge_status)
        except ValueError as e:
            self._logger.error(
                f'An error ocurred while trying to look an outage ticket up for edge {edge_identifier}. '
                f'Skipping edge for now... Cause: {e}'
            )
            message = (
                f"[process-quarantine-edge] An error ocurred while trying to look an outage ticket "
                f"up for edge {edge_identifier}. Skipping edge for now... Cause: {e}"
            )
            slack_message = {'request_id': uuid(),
                             'message': message}
            await self._event_bus.rpc_request("notification.slack.request", slack_message, timeout=30)
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

        edge_has_ticket = outage_ticket['body'] is not None
        if edge_has_ticket:
            return False

        return True

    async def _get_edge_status_by_id(self, edge_full_id):
        edge_status_request_dict = {
            'request_id': uuid(),
            'body': edge_full_id,
        }
        edge_status_response = await self._event_bus.rpc_request(
            'edge.status.request', edge_status_request_dict, timeout=120,
        )

        return edge_status_response

    async def _get_outage_ticket_for_edge(self, edge_status: dict, ticket_statuses=None):
        edge_serial = edge_status['edges']['serialNumber']
        enterprise_name = edge_status['enterprise_name']
        client_id = self._extract_client_id(enterprise_name)

        outage_ticket_request = {'request_id': uuid(), 'body': {'edge_serial': edge_serial, 'client_id': client_id}}

        if ticket_statuses is not None:
            outage_ticket_request['body']['ticket_statuses'] = ticket_statuses

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

    async def _get_management_status(self, edge_status):
        enterprise_name = edge_status['enterprise_name']
        bruin_client_id = self._extract_client_id(enterprise_name)
        serial_number = edge_status['edges']['serialNumber']
        management_request = {
            "request_id": uuid(),
            "body": {
                "client_id": bruin_client_id,
                "status": "A",
                "service_number": serial_number
            }
        }

        management_status = await self._event_bus.rpc_request("bruin.inventory.management.status",
                                                              management_request, timeout=30)

        return management_status

    def _is_management_status_active(self, management_status) -> bool:
        return management_status in {"Pending", "Active – Gold Monitoring", "Active – Platinum Monitoring"}
