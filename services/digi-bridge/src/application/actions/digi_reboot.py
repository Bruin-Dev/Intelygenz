import json


class DiGiReboot:

    def __init__(self, logger, event_bus, digi_repository):
        self._logger = logger
        self._event_bus = event_bus
        self._digi_repository = digi_repository

    async def digi_reboot(self, msg: dict):
        request_id = msg['request_id']
        response_topic = msg['response_topic']
        response = {
            'request_id': request_id,
            'body': None,
            'status': None
        }
        if "body" not in msg.keys():
            self._logger.error(f'Cannot reboot DiGi client using {json.dumps(msg)}. '
                               f'JSON malformed')
            response["status"] = 400
            response["body"] = 'Must include "body" in request'
            await self._event_bus.publish_message(response_topic, response)
            return

        payload = msg['body']

        if not all(key in payload.keys() for key in ("velo_serial", "ticket", "MAC")):
            self._logger.error(f'Cannot reboot DiGi client using {json.dumps(msg)}. '
                               f'JSON malformed')

            response["body"] = 'You must include "velo_serial", "ticket", "MAC" ' \
                               'in the "body" field of the response request'
            response["status"] = 400
            await self._event_bus.publish_message(msg['response_topic'], response)
            return

        payload["igzID"] = request_id

        self._logger.info(f'Attempting to reboot DiGi client with payload of: {json.dumps(payload)}')

        results = await self._digi_repository.reboot(payload)

        response["body"] = results['body']
        response["status"] = results['status']

        await self._event_bus.publish_message(response_topic, response)
        self._logger.info(
            f'DiGi reboot process completed and publishing results in event bus for request {json.dumps(msg)}. '
            f"Message published was {response}"
        )
