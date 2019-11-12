import json

from datetime import datetime

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
