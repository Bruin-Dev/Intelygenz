from igz.packages.eventbus.eventbus import EventBus
from datetime import datetime, timedelta, timezone


class ReportEdgeStatus:

    def __init__(self, config, event_bus: EventBus, velocloud_repository, logger):
        self._configs = config
        self._event_bus = event_bus
        self._velocloud_repository = velocloud_repository
        self._logger = logger

    async def report_edge_status(self, msg: dict):
        request_id = msg["request_id"]
        edge_status_values = ["enterprise_name", "edges", "links"]
        interval = {
            "start": (datetime.now() - timedelta(hours=8)).replace(tzinfo=timezone.utc).isoformat()
        }
        is_body = msg.get("body") is not None

        if is_body:
            interval = msg["body"]["interval"] if msg["body"].get("interval") else interval
        status_code = 200

        self._logger.info(f'Processing edge with data {msg}')
        body_content = None
        if not msg.get("body"):
            status_code = 500
            self._logger.info(f"msg hasn't body content: {msg}")
        else:
            edgeids = msg["body"]
            enterprise_name = self._velocloud_repository.get_enterprise_information(edgeids)
            edge_status_vr = self._velocloud_repository.get_edge_information(edgeids)
            link_status = self._velocloud_repository.get_link_information(edgeids, interval)
            status_list = (enterprise_name["status_code"], edge_status_vr["status_code"], link_status["status_code"])
            body = [enterprise_name["body"], edge_status_vr["body"], link_status["body"]]
            if not all(status in range(200, 300) for status in status_list):
                self._logger.info("It wasn't possible to get enterprise, edge or link information")
                status_code = 500
            edge_status = dict(zip(edge_status_values, body))
            body_content = {"edge_id": edgeids, "edge_info": edge_status}

        edge_response = {"request_id": request_id, "body": body_content, "status": status_code}
        self._logger.info(f'Response {edge_response} was published in ')
        await self._event_bus.publish_message(msg['response_topic'], edge_response)
