from igz.packages.eventbus.eventbus import EventBus


class EnterpriseNameList:

    def __init__(self, event_bus: EventBus, velocloud_repository, logger):
        self._event_bus = event_bus
        self._velocloud_repository = velocloud_repository
        self._logger = logger

    async def enterprise_name_list(self, msg):
        self._logger.info("Sending enterprise name list")
        # Check if body exists
        enterprise_name_list_response = {
            "request_id": msg['request_id'],
            "body": None,
            "status": None
        }

        if msg.get("body") is None:
            enterprise_name_list_response["status"] = 400
            enterprise_name_list_response["body"] = 'Must include "body" in request'
            await self._event_bus.publish_message(msg['response_topic'], enterprise_name_list_response)
            return

        enterprise_names = self._velocloud_repository.get_all_enterprise_names(msg["body"])

        enterprise_name_list_response["body"] = enterprise_names["body"]

        enterprise_name_list_response["status"] = enterprise_names["status"]

        await self._event_bus.publish_message(msg['response_topic'], enterprise_name_list_response)
        self._logger.info("Enterprise name list sent")
