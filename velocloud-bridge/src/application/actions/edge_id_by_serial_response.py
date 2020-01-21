import json
from igz.packages.eventbus.eventbus import EventBus


class SearchForIDsBySerial:

    def __init__(self, config, event_bus: EventBus, logger, ids_by_serial_repository):
        self._config = config
        self._event_bus = event_bus
        self._logger = logger
        self._ids_by_serial_repository = ids_by_serial_repository

    async def search_for_edge_id(self, msg):
        serial = msg['serial']

        self._logger.info(f'Searching for edge_id for serial number {serial}')
        edge_id = self._ids_by_serial_repository.search_for_edge_id_by_serial(serial)

        status = 200
        if edge_id is None:
            status = 204
        if isinstance(edge_id, Exception):
            status = 500

        edge_id_response = {"request_id": msg['request_id'], "edge_id": edge_id, "status": status}
        await self._event_bus.publish_message(msg['response_topic'], edge_id_response)
        self._logger.info("Edge id sent")
