class SaveCreatedTicketFeedback:
    def __init__(self, logger, config, event_bus, repository):
        self._config = config
        self._logger = logger
        self._event_bus = event_bus
        self._kre_repository = repository

    async def save_created_ticket_feedback(self, msg: dict):
        """Save the feedback for created tickets

        Args:
            msg (dict): The request.
        """
        response = {
            "request_id": msg["request_id"],
            "body": "",
            "status": 0,
        }

        response_topic = msg["response_topic"]

        msg_body = msg.get("body", {})
        ticket_id = msg_body.get("ticket_id")
        if not msg_body or not ticket_id:
            self._logger.error(f"Error cannot save feedback for ticket: {ticket_id}. error JSON malformed")
            response["body"] = "You must use correct format in the request"
            response["status"] = 400
            await self._event_bus.publish_message(response_topic, response)
            return

        save_create_tickets_response = await self._kre_repository.save_created_ticket_feedback(msg_body)
        response["body"] = save_create_tickets_response["body"]
        response["status"] = save_create_tickets_response["status"]

        await self._event_bus.publish_message(msg["response_topic"], response)
        self._logger.info(f"Save created tickets result for ticket {ticket_id} published in event bus!")
