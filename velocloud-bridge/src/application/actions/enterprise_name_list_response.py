from igz.packages.eventbus.eventbus import EventBus
import json


class EnterpriseNameList:

    def __init__(self, event_bus: EventBus, velocloud_repository, logger):
        self._event_bus = event_bus
        self._velocloud_repository = velocloud_repository
        self._logger = logger

    async def enterprise_name_list(self, msg):
        msg = json.loads(msg)
        self._logger.info("Sending enterprise name list")
        enterprise_names = self._velocloud_repository.get_all_enterprise_names(msg)

        status = 200
        if enterprise_names is None:
            status = 204
        if isinstance(enterprise_names, Exception):
            status = 500

        enterprise_name_list_response = {
            "request_id": msg['request_id'],
            "enterprise_names": enterprise_names,
            "status": status
        }
        await self._event_bus.publish_message(
            msg['response_topic'],
            json.dumps(enterprise_name_list_response, default=str)
        )
        self._logger.info("Enterprise name list sent")
