class HandleTicketForward:
    def __init__(self, metrics_repository, bruin_repository):
        self._metrics_repository = metrics_repository
        self._bruin_repository = bruin_repository

    async def success(self, msg: dict):
        self._metrics_repository.increment_tasks_forwarded(**msg["metrics_labels"])
