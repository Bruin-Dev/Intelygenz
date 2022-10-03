class HandleTicketForward:
    def __init__(self, logger, metrics_repository, bruin_repository):
        self._logger = logger
        self._metrics_repository = metrics_repository
        self._bruin_repository = bruin_repository

    async def success(self, msg: dict):
        ticket_id = msg["ticket_id"]
        serial_number = msg["serial_number"]
        target_queue = msg["target_queue"]

        self._logger.info(f"Successfully forwarded ticket {ticket_id} and serial {serial_number} to {target_queue}")
        self._metrics_repository.increment_tasks_forwarded(**msg["metrics_labels"])
