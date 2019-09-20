import json
from datetime import datetime

from apscheduler.util import undefined
from pytz import timezone
from shortuuid import uuid

from igz.packages.eventbus.eventbus import EventBus


class EdgeMonitoring:

    def __init__(self, event_bus: EventBus, logger, prometheus_repository, scheduler, edge_repository,
                 status_repository, statistic_repository, service_id, config):
        self._event_bus = event_bus
        self._logger = logger
        self._prometheus_repository = prometheus_repository
        self._scheduler = scheduler
        self._edge_repository = edge_repository
        self._status_repository = status_repository
        self._statistic_repository = statistic_repository
        self._service_id = service_id
        self._config = config

    async def _edge_monitoring_process(self):
        self._logger.info("Starting velocloud edge monitoring process")
        if "PROCESSING_VELOCLOUD_EDGES" in self._status_repository.get_status():
            edges_processed = self._status_repository.get_edges_processed()
            edges_to_process = self._status_repository.get_edges_to_process()
            self._logger.error(f'There\'s still edges to be processed: {edges_processed} / {edges_to_process}')

            cycle_seconds = self._config.ORCHESTRATOR_CONFIG['monitoring_seconds']
            current_cycle_timestamp = self._status_repository.get_current_cycle_timestamp()

            if datetime.timestamp(datetime.now()) - current_cycle_timestamp > cycle_seconds:
                self._status_repository.set_status("IDLE")
                self._logger.info('Time since current cycle exceeds threshold, triggering process again')
            else:
                self._logger.error('Edge monitoring process won\'t be triggered again')
        if "IDLE" in self._status_repository.get_status():
            self._logger.info("IDLE status: asking edge list. Orchestrator status = REQUESTING_VELOCLOUD_EDGES...")
            self._status_repository.set_status("REQUESTING_VELOCLOUD_EDGES")
            self._status_repository.set_edges_processed(0)
            # await self._send_stats_to_notifier()
            self._statistic_repository._statistic_client.clear_dictionaries()
            self._status_repository.set_current_cycle_timestamp(datetime.timestamp(datetime.now()))
            await self._request_edges(uuid())
            self._logger.info("Sending edge status tasks. Orchestrator status = PROCESSING_VELOCLOUD_EDGES...")
            self._status_repository.set_status("PROCESSING_VELOCLOUD_EDGES")

    async def start_edge_monitor_job(self, exec_on_start=False):
        seconds = self._config.ORCHESTRATOR_CONFIG['monitoring_seconds']
        self._logger.info(f'Scheduled task: edge monitoring process configured to run each {seconds} seconds')
        next_run_time = undefined
        if exec_on_start:
            next_run_time = datetime.now(timezone('US/Eastern'))
            self._logger.info(f'It will be executed now')
        self._scheduler.add_job(self._edge_monitoring_process, 'interval', seconds=seconds, next_run_time=next_run_time,
                                replace_existing=True, id='_edge_monitoring_process')

    async def _send_stats_to_notifier(self):
        current_cycle_request_id = self._status_repository.get_current_cycle_request_id()
        redis_keys = [redis_edge for redis_edge in self._edge_repository.get_keys() if 'host' in redis_edge]
        for redis_edge in redis_keys:
            redis_data = json.loads(self._edge_repository.get_edge(redis_edge))
            if redis_data["request_id"] == current_cycle_request_id:
                if redis_data["redis_edge"]["edges"]["edgeState"] == 'CONNECTED':
                    self._logger.info('Edge seems OK')
                else:
                    self._logger.error('Edge seems KO, failure!')
                    self._statistic_repository.store_stats(redis_data["redis_edge"])

        slack_msg = self._statistic_repository._statistic_client.get_statistics()
        if slack_msg is not None:
            msg = dict(request_id=current_cycle_request_id,
                       response_topic=f'notification.slack.request.{self._service_id}',
                       message=slack_msg)
            await self._event_bus.publish_message("notification.slack.request", json.dumps(msg))
        else:
            self._logger.error("No statistics present")

    async def _request_edges(self, request_id):
        msg = dict(request_id=request_id, response_topic=f'edge.list.response.{self._service_id}', filter=[])
        self._status_repository.set_current_cycle_request_id(request_id)
        await self._event_bus.publish_message("edge.list.request", json.dumps(msg))

    async def receive_edge_list(self, msg):
        self._logger.info(f'Edge list received from event bus')
        decoded_msg = json.loads(msg)
        edge_status_requests = [
            dict(request_id=decoded_msg["request_id"], response_topic=f'edge.status.response.{self._service_id}',
                 edge=edge) for edge in decoded_msg["edges"]]
        self._prometheus_repository.set_cycle_total_edges(len(edge_status_requests))
        self._status_repository.set_edges_to_process(len(edge_status_requests))

        redis_edge_list = self._edge_repository.get_last_edge_list()
        if redis_edge_list is not None:
            decoded_redis_edge_list = json.loads(redis_edge_list)
            if len(decoded_redis_edge_list) != len(decoded_msg["edges"]):
                for redis_edge in decoded_redis_edge_list:
                    if redis_edge not in decoded_msg['edges']:
                        redis_edge_info = json.loads(self._edge_repository.get_edge(str(redis_edge)))
                        self._prometheus_repository.dec(redis_edge_info["redis_edge"])

        self._edge_repository.set_current_edge_list(json.dumps(decoded_msg["edges"]))

        self._logger.info(f'Splitting and sending edges to the event bus')
        for request in edge_status_requests:
            await self._event_bus.publish_message("edge.status.request", json.dumps(request))
        self._logger.info(f'Requests sent')

    async def receive_edge(self, msg):
        self._logger.info(f'Edge received from event bus')
        edge = json.loads(msg)
        self._logger.info(f'Edge data: {json.dumps(edge, indent=2)}')
        edges_processed = self._status_repository.get_edges_processed()
        edges_to_process = self._status_repository.get_edges_to_process()
        edges_processed = edges_processed + 1
        self._status_repository.set_edges_processed(edges_processed)

        redis_edge = self._edge_repository.get_edge(str(edge['edge_id']))
        if redis_edge is None:
            self._prometheus_repository.inc(edge['edge_info'])
        else:
            redis_edge_data = json.loads(redis_edge)
            if redis_edge_data['redis_edge']['edges']['edgeState'] != edge['edge_info']['edges']['edgeState']:
                self._prometheus_repository.update_edge(edge['edge_info'], redis_edge_data['redis_edge'])

            for link, redis_link in zip(edge['edge_info']['links'], redis_edge_data['redis_edge']['links']):
                if link['link']['state'] != redis_link['link']['state']:
                    self._prometheus_repository.update_link(edge['edge_info'], link,
                                                            redis_edge_data['redis_edge'], redis_link)

        redis_data = {"request_id": edge["request_id"], "redis_edge": edge['edge_info']}
        self._edge_repository.set_edge(edge['edge_id'], json.dumps(redis_data))
        self._logger.info(f'Edges processed: {edges_processed} / {edges_to_process}')
        if edges_processed == edges_to_process:
            self._logger.info("All edges processed, starting the cycle again")
            self._status_repository.set_status("IDLE")
            await self._edge_monitoring_process()

    def start_prometheus_metrics_server(self):
        self._prometheus_repository.start_prometheus_metrics_server()
