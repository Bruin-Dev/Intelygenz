from igz.packages.eventbus.eventbus import EventBus


class EnterpriseNameList:

    def __init__(self, event_bus: EventBus, velocloud_repository, logger):
        self._event_bus = event_bus
        self._velocloud_repository = velocloud_repository
        self._logger = logger

    async def enterprise_name_list(self, msg):
        self._logger.info("Sending enterprise name list")
        enterprise_names = self._velocloud_repository.get_all_enterprise_names(msg["body"])

        if enterprise_names["status_code"] == 500:
            self._logger.error("Fail to get the list of enterprise names")

        enterprise_name_list_response = {
            "request_id": msg['request_id'],
            "body": enterprise_names["body"],
            "status": enterprise_names["status_code"]
        }
        await self._event_bus.publish_message(msg['response_topic'], enterprise_name_list_response)
        self._logger.info("Enterprise name list sent")
