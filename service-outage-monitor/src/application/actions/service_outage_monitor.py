import base64
import json
import re
from collections import OrderedDict
from datetime import datetime, timedelta

from apscheduler.util import undefined
from pytz import timezone, utc
from shortuuid import uuid

from igz.packages.eventbus.eventbus import EventBus


class ServiceOutageMonitor:

    def __init__(self, event_bus: EventBus, logger, scheduler, config, template_renderer):
        self._event_bus = event_bus
        self._logger = logger
        self._scheduler = scheduler
        self._config = config
        self._template_renderer = template_renderer

    async def start_service_outage_monitor_job(self, exec_on_start=False):
        self._logger.info(f'Scheduled task: service outage')
        next_run_time = undefined
        if exec_on_start:
            next_run_time = datetime.now(timezone('US/Eastern'))
            self._logger.info(f'It will be executed now')
        self._scheduler.add_job(self._service_outage_monitor_process, 'interval', seconds=900,
                                next_run_time=next_run_time, replace_existing=True,
                                id='_service_outage_monitor_process')

    async def _service_outage_monitor_process(self):
        edge_list_request = {'request_id': uuid(),
                             'filter': [{'host': 'mettel.velocloud.net', 'enterprise_ids': []},
                                        {'host': 'metvco03.mettel.net', 'enterprise_ids': []},
                                        {'host': 'metvco04.mettel.net', 'enterprise_ids': []}]}
        edge_list = await self._event_bus.rpc_request("edge.list.request", json.dumps(edge_list_request), timeout=60)
        self._logger.info(f'Edge list received from event bus')
        self._logger.info(f'Splitting and sending edges to the event bus')
        for edge in edge_list['edges']:
            edge_status_request = {'request_id': uuid(),
                                   'edge': edge}
            edge_status = await self._event_bus.rpc_request("edge.status.request", json.dumps(edge_status_request),
                                                            timeout=45)
            self._logger.info(f'Edge received from event bus')
            if edge_status["edge_info"]["edges"]["edgeState"] == 'CONNECTED':
                self._logger.info('Edge seems OK')
            elif edge_status["edge_info"]["edges"]["edgeState"] == 'OFFLINE':
                self._logger.error('Edge seems KO, failure!')
                # TODO remove production check here when production part gets implemented
                if self._config.MONITOR_CONFIG['environment'] == 'dev' or self._config.MONITOR_CONFIG['environment'] \
                                                              == 'production':
                    events_msg = {'request_id': uuid(),
                                  'edge': edge_status['edge_id'],
                                  'start_date': (datetime.now(utc) - timedelta(days=7)),
                                  'end_date': datetime.now(utc)}
                    edge_events = await self._event_bus.rpc_request("alert.request.event.edge",
                                                                    json.dumps(events_msg, default=str), timeout=10)
                    email_obj = self._template_renderer._compose_email_object(edge_status, edge_events)
                    await self._event_bus.rpc_request("notification.email.request", json.dumps(email_obj), timeout=10)
                # elif self._config.MONITOR_CONFIG['environment'] == 'production':
                #     TODO create repair tickets
                #     pass
        # Start up the next job
        self._logger.info("End of service outage monitor job")

    def _find_recent_occurence_of_event(self, event_list, event_type, message=None):
        for event_obj in event_list:
            if event_obj['event'] == event_type:
                if message is not None:
                    if event_obj['message'] == message:
                        return event_obj['eventTime']
                else:
                    return event_obj['eventTime']
        return None
