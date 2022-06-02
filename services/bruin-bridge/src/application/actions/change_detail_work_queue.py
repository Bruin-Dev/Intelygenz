import json


class ChangeDetailWorkQueue:
    def __init__(self, logger, event_bus, bruin_repository):
        self._logger = logger
        self._event_bus = event_bus
        self._bruin_repository = bruin_repository

    async def change_detail_work_queue(self, msg: dict):
        request_id = msg["request_id"]
        response_topic = msg["response_topic"]
        response = {"request_id": request_id, "body": None, "status": None}

        msg_body = msg.get("body")
        if not msg_body:
            self._logger.error(f"Cannot change detail work queue using {json.dumps(msg)}. JSON malformed")
            response["body"] = (
                'You must specify {.."body": {"service_number", "ticket_id", "detail_id", "queue_name"}..} '
                "in the request"
            )
            response["status"] = 400
            await self._event_bus.publish_message(response_topic, response)
            return

        if not all(key in msg_body.keys() for key in ("ticket_id", "queue_name")) or not any(
            key in msg_body.keys() for key in ("service_number", "detail_id")
        ):
            self._logger.error(
                f"Cannot change detail work queue using {json.dumps(msg_body)}. "
                f'Need all these parameters: "service_number" or "detail_id", "ticket_id", "queue_name"'
            )
            response["body"] = (
                'You must specify {.."body": {"service_number" or "detail_id", "ticket_id", "queue_name"}..} '
                "in the request"
            )
            response["status"] = 400
            await self._event_bus.publish_message(response_topic, response)
            return

        ticket_id = msg_body.pop("ticket_id")
        self._logger.info(f"Changing work queue of ticket {ticket_id} with filters: {json.dumps(msg_body)}")

        result = await self._bruin_repository.change_detail_work_queue(ticket_id, filters=msg_body)

        response["body"] = result["body"]
        response["status"] = result["status"]
        await self._event_bus.publish_message(response_topic, response)

        self._logger.info(
            f"Result of changing work queue of ticket {ticket_id} with filters {json.dumps(msg_body)} "
            "published in event bus!"
        )
