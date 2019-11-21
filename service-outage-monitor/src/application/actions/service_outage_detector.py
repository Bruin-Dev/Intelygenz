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

    def __init__(self, event_bus, logger, scheduler, quarantine_edge_repository, reporting_edge_repository, config):
        self._event_bus = event_bus
        self._logger = logger
        self._scheduler = scheduler
        self._reporting_edge_repository = reporting_edge_repository
        self._quarantine_edge_repository = quarantine_edge_repository
        self._config = config

    async def load_persisted_quarantine(self):
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
            replace_existing=False,  # Allows to preserve the timestamp of the first detection if the edge is already
                                     # in quarantine
            time_to_live=edge_ttl)

        self._logger(f'Edge {edge_identifier} sent to quarantine')

    def _is_there_an_outage(self, edge_status):
        is_edge_offline = edge_status["edges"]["edgeState"] == 'OFFLINE'
        is_any_link_disconnected = any(
            link_status['link']['state'] == 'DISCONNECTED'
            for link_status in edge_status['links']
        )

        return is_edge_offline or is_any_link_disconnected

    async def _service_outage_reporter_process(self):
        email_report = self._edge_repository_template_renderer._compose_email_object()
        await self._event_bus.rpc_request("notification.email.request",
                                          json.dumps(email_report),
                                          timeout=10)
        self._reporting_edge_repository.reset_root_key()

    async def _get_all_edges(self):
        edge_list_request_dict = {
            'request_id': uuid(),
            'filter': [
                {'host': 'mettel.velocloud.net', 'enterprise_ids': []},
                {'host': 'metvco03.mettel.net', 'enterprise_ids': []},
                {'host': 'metvco04.mettel.net', 'enterprise_ids': []},
            ]
        }
        edge_list_response = await self._event_bus.rpc_request(
            'edge.list.request',
            json.dumps(edge_list_request_dict),
            # TODO: Probably will take 4-6 minutes, check in local
            timeout=60,
        )

        return edge_list_response['edges']

    async def _process_edge_from_quarantine(self, edge_full_id):
        edge_identifier = EdgeIdentifier(**edge_full_id)
        edge_status = await self._get_edge_status_by_id(edge_full_id)

        if self._is_there_an_outage(edge_status):
            outage_ticket = await self._get_outage_ticket_for_edge(edge_full_id)

            if outage_ticket is None:
                self._add_edge_to_reporting(edge_full_id, edge_status)
            else:
                self._logger(
                    f'Edge {edge_identifier} has an outage but there is already '
                    'an outage ticket created for it. This edge will not be reported.'
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
        edge_serial = edge_value['edge_status']['edges']['serialNumber']
        enterprise_name = edge_value['edge_status']['enterprise_name']
        client_id = self._extract_client_id(enterprise_name)

        outage_ticket_request = {'request_id': uuid(), 'edge_serial': edge_serial, 'client_id': client_id}
        outage_ticket = await self._event_bus.rpc_request(
            'bruin.ticket.outage.details.by_edge_serial.request',
            json.dumps(outage_ticket_request),
        )

        return outage_ticket

    def _extract_client_id(self, enterprise_name):
        client_id_match = self.__client_id_regex.match(enterprise_name)

        if client_id_match:
            client_id = client_id_match.group('client_id')
            return client_id

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

        self._reporting_edge_repository.add_edge(edge_full_id, edge_status_for_reporting)
        self._quarantine_edge_repository.remove_edge(edge_full_id)

        self._logger.info(f'Edge {edge_identifier} moved from quarantine to the reporting queue.')
