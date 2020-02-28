from igz.packages.eventbus.eventbus import EventBus


class ReportEdgeList:

    def __init__(self, config, event_bus: EventBus, velocloud_repository, logger):
        self._configs = config
        self._event_bus = event_bus
        self._velocloud_repository = velocloud_repository
        self._logger = logger

    async def report_edge_list(self, msg: dict):
        self._logger.info("Sending edge list")
        self._logger.info(
            f'Getting edge list with host'
        )
        if not msg.get('body'):
            edges_by_enterprise = {"body": None, "status": 500}
            self._logger.info(f"msg hasn't body content: {msg}")
        else:
            edges_by_enterprise = self._velocloud_repository.get_all_enterprises_edges_with_host(msg['body'])

        edge_list_response = {"request_id": msg['request_id'],
                              **edges_by_enterprise}
        await self._event_bus.publish_message(msg['response_topic'], edge_list_response)
        self._logger.info("Edge list sent")
