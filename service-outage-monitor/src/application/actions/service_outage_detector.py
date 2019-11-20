import json
from datetime import datetime
from datetime import timedelta

from apscheduler.jobstores.base import ConflictingIdError
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
        self._load_quarantine_from_redis()

    def _load_quarantine_from_redis(self):
        # Get all the edges in quarantine from redis. Schedule a quarantine job 10 minutes after detection_time
        pass

    async def start_service_outage_detector_job(self, exec_on_start=False):
        self._logger.info('Scheduling Service Outage Detector job...')
        next_run_time = undefined

        if exec_on_start:
            tz = timezone(self._config.MONITOR_CONFIG['timezone'])
            next_run_time = datetime.now(tz)
            self._logger.info('Service Outage Detector job is going to be executed immediately')
        try:
            self._scheduler.add_job(self._service_outage_detector_process, 'interval',
                                    seconds=self._config.MONITOR_CONFIG['outage_detector_minutes'],
                                    next_run_time=next_run_time, replace_existing=False,
                                    id='_service_outage_detector_process')
        except ConflictingIdError as conflict:
            self._logger.info(f'Skipping start of detector process. Reason: {conflict}')

    async def _service_outage_detector_process(self):
        self._logger.info(
            'Triggering new Service Outage Detector job. Current datetime is '
            f'{datetime.now(timezone(self._config.MONITOR_CONFIG["timezone"]))}'
        )

        edge_list = await self._get_all_edges()
        for edge_full_id in edge_list:
            edge_status = await self._get_edge_status_by_id(edge_full_id)
            # if outage
            # Schedule quarantine job

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
            # Probably will take 4-6 minutes, check in local
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
        # Outage is EDGE == OFFLINE or any of the links == DISCONNECTED (you can double check the names in grafana)
        return edge_status["edges"]["edgeState"] == 'OFFLINE'

    async def start_quarantine_job(self, edge_id):
        # make run_date a parameter for using the same function for recovery
        self._logger.info(f'Edge put in quarantine, with ids: {edge_id}')
        tz = timezone(self._config.MONITOR_CONFIG['timezone'])
        run_date = datetime.now(tz) + timedelta(minutes=self._config.MONITOR_CONFIG['quarantine_minutes'])
        detection_time = datetime.now(tz)
        try:
            self._scheduler.add_job(self._quarantine_edge, 'date',
                                    run_date=run_date, replace_existing=False, misfire_grace_time=9999,
                                    id=f'_quarantine:{json.dumps(edge_id)}', args=[self, edge_id, detection_time])
        except ConflictingIdError as conflict:
            self._logger.info(f'Skipping add quarantine job. Reason: {conflict}')

        # Put in redis with expiration = outage_time + 5 minutes, and detection time

    async def _quarantine_edge(self, edge_id, detection_time):
        # get edge
        # outage == self._is_offline(edge["edge_status"])
        # if outage:
        await self._get_outage_ticket_for_edge(edge_id)
        # if outage_ticket is None:
        # add edge_to_reporting(edge, detection_time)

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

    async def start_service_outage_reporter_job(self, exec_on_start=False):
        # This report happens each hour
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

    async def _service_outage_reporter_process(self):
        email_report = self._edge_repository_template_renderer._compose_email_object()
        await self._event_bus.rpc_request("notification.email.request",
                                          json.dumps(email_report),
                                          timeout=10)
        self._reporting_edge_repository.reset_root_key()
