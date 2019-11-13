import json
import re

from datetime import datetime
from datetime import timedelta

from apscheduler.util import undefined
from pytz import timezone
from shortuuid import uuid


class ServiceOutageDetector:
    def __init__(self, event_bus, logger, scheduler, online_edge_repository, quarantine_edge_repository, config):
        self._event_bus = event_bus
        self._logger = logger
        self._scheduler = scheduler
        self._online_edge_repository = online_edge_repository
        self._quarantine_edge_repository = quarantine_edge_repository
        self._config = config

    async def start_service_outage_detector_job(self, exec_on_start=False):
        self._logger.info('Scheduling Service Outage Detector job...')
        next_run_time = undefined

        if exec_on_start:
            tz = timezone(self._config.MONITOR_CONFIG['timezone'])
            next_run_time = datetime.now(tz)
            self._logger.info('Service Outage Detector job is going to be executed immediately')

        self._scheduler.add_job(self._service_outage_detector_process, 'interval',
                                seconds=self._config.MONITOR_CONFIG['jobs_intervals']['outage_detector'],
                                next_run_time=next_run_time, replace_existing=True,
                                id='_service_outage_detector_process')

    async def _service_outage_detector_process(self):
        self._logger.info(
            'Triggering new Service Outage Detector job. Current datetime is '
            f'{datetime.now(timezone(self._config.MONITOR_CONFIG["timezone"]))}'
        )

        edge_list = await self._get_all_edges()
        for edge_full_id in edge_list:
            edge_status = await self._get_edge_status_by_id(edge_full_id)

            if self._is_offline(edge_status):
                self._quarantine_edge_repository.add_edge(full_id=edge_full_id, status=edge_status, time_to_live=600)
            else:
                self._online_edge_repository.add_edge(full_id=edge_full_id, status=edge_status, time_to_live=600)

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
            timeout=60,
        )

        return edge_list_response['edges']

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

    def _is_offline(self, edge_status):
        return edge_status["edges"]["edgeState"] == 'OFFLINE'


class DetectedOutagesObserver:
    __client_id_regex = re.compile(r'^.*\|(?P<client_id>\d+)\|$')

    def __init__(self, event_bus, logger, scheduler, online_edge_repository,
                 quarantine_edge_repository, reporting_edge_repository, config):
        self._event_bus = event_bus
        self._logger = logger
        self._scheduler = scheduler
        self._online_edge_repository = online_edge_repository
        self._quarantine_edge_repository = quarantine_edge_repository
        self._reporting_edge_repository = reporting_edge_repository
        self._config = config

    async def start_detected_outages_observer_job(self, exec_on_start=False):
        self._logger.info('Scheduling Detected Outages Observer job...')
        next_run_time = undefined

        if exec_on_start:
            tz = timezone(self._config.MONITOR_CONFIG['timezone'])
            next_run_time = datetime.now(tz)
            self._logger.info('Detected Outages Observer job is going to be executed immediately')

        self._scheduler.add_job(self._observe_detected_outages, 'interval',
                                seconds=self._config.MONITOR_CONFIG['jobs_intervals']['outage_observer'],
                                next_run_time=next_run_time, replace_existing=True,
                                id='_detected_outages_observer_process')

    async def _observe_detected_outages(self):
        self._purge_edge_stores()
        await self._process_quarantine()

    def _purge_edge_stores(self):
        online_edges = self._online_edge_repository.get_all_edges()
        online_edges_full_id_as_str_list = online_edges.keys()

        self._remove_online_edges_from_quarantine(online_edges_full_id_as_str_list)
        self._remove_online_edges_from_edges_to_report(online_edges_full_id_as_str_list)
        self._clear_online_edges_store()

    def _remove_online_edges_from_quarantine(self, full_id_as_str_set):
        self._quarantine_edge_repository.remove_edge_set(*full_id_as_str_set)

    def _remove_online_edges_from_edges_to_report(self, full_id_as_str_set):
        self._reporting_edge_repository.remove_edge_set(*full_id_as_str_set)

    def _clear_online_edges_store(self):
        self._online_edge_repository.reset_root_key()

    async def _process_quarantine(self):
        quarantine_edges = self._quarantine_edge_repository.get_all_edges()
        edges_to_report = {}

        for edge_identifier, value in quarantine_edges.items():
            if self._is_there_an_outage(value):
                outage_ticket = await self._get_outage_ticket_for_edge(value)

                if outage_ticket:
                    value['ticketID'] = outage_ticket['ticketID']
                else:
                    value['ticketID'] = None

                edges_to_report[edge_identifier] = value

        self._move_edges_to_reporting(edges_to_report)

    def _is_there_an_outage(self, edge_value: dict):
        outage_period = timedelta(minutes=40)

        quarantine_addition_timestamp = edge_value['addition_timestamp']
        quarantine_addition_datetime = datetime.fromtimestamp(quarantine_addition_timestamp)

        return (datetime.now() - quarantine_addition_datetime) > outage_period

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

    def _move_edges_to_reporting(self, edges: dict):
        self._quarantine_edge_repository.reset_root_key()
        self._reporting_edge_repository.add_edge_set(edges)

    def _extract_client_id(self, enterprise_name):
        client_id_match = self.__client_id_regex.match(enterprise_name)

        if client_id_match:
            client_id = client_id_match.group('client_id')
            return client_id
