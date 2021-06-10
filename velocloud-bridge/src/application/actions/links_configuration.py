class LinksConfiguration:

    def __init__(self, event_bus, velocloud_repository, logger):
        self._event_bus = event_bus
        self._velocloud_repository = velocloud_repository
        self._logger = logger

    async def links_configuration(self, msg: dict):
        edge_config_module_request = {
            "request_id": msg['request_id'],
            "body": None,
            "status": None
        }

        if msg.get("body") is None:
            edge_config_module_request["status"] = 400
            edge_config_module_request["body"] = 'Must include "body" in request'
            await self._event_bus.publish_message(msg['response_topic'], edge_config_module_request)
            return

        if not all(key in msg['body'].keys() for key in ("host", "enterprise_id", "edge_id")):
            edge_config_module_request["status"] = 400
            edge_config_module_request["body"] = 'You must specify ' \
                                                 '{..."body": {"host", "enterprise_id", "edge_id"}...} in the request'
        else:
            edge_full_id = msg['body']
            config_response = await self._velocloud_repository.get_links_configuration(edge_full_id)
            edge_config_module_request["status"] = config_response['status']
            edge_config_module_request["body"] = config_response['body']

        await self._event_bus.publish_message(msg['response_topic'], edge_config_module_request)
