import logging
from datetime import datetime

from apscheduler.jobstores.base import ConflictingIdError
from framework.storage.task_dispatcher_client import TaskTypes
from pytz import timezone

from application.repositories.utils_repository import to_json_bytes

logger = logging.getLogger(__name__)


class TaskDispatcher:
    def __init__(
        self,
        nats_client,
        scheduler,
        task_dispatcher_client,
        config,
        bruin_repository,
    ):
        self._nats_client = nats_client
        self._scheduler = scheduler
        self._task_dispatcher_client = task_dispatcher_client
        self._config = config
        self._bruin_repository = bruin_repository

    async def start_dispatching(self):
        logger.info("Scheduling Task Dispatcher job...")
        tz = timezone(self._config.TIMEZONE)
        next_run_time = datetime.now(tz)

        try:
            self._scheduler.add_job(
                self._dispatch_due_tasks,
                "interval",
                seconds=self._config.DISPATCH_CONFIG["interval"],
                next_run_time=next_run_time,
                replace_existing=False,
                id="_dispatch_process",
            )
        except ConflictingIdError as conflict:
            logger.info(f"Skipping start of Task Dispatcher job. Reason: {conflict}")

    async def _dispatch_due_tasks(self):
        logger.info("Getting due tasks...")

        ticket_forward_tasks = self._task_dispatcher_client.get_due_tasks(TaskTypes.TICKET_FORWARDS)
        due_tasks = ticket_forward_tasks

        if due_tasks:
            logger.info(f"{len(due_tasks)} due task(s) found")
        else:
            logger.info("No due tasks were found")

        for task in due_tasks:
            try:
                await self._dispatch_task(task)
            except Exception as e:
                logger.exception(e)

        if due_tasks:
            logger.info("Finished dispatching due tasks!")

    async def _dispatch_task(self, task: dict):
        logger.info(f"Dispatching task of type {task['type'].value} for key {task['key']}...")
        success = False

        if task["type"] == TaskTypes.TICKET_FORWARDS:
            success = await self._forward_ticket(**task["data"])

        result = "success" if success else "error"
        await self._nats_client.publish(f"task_dispatcher.{task['type'].value}.{result}", to_json_bytes(task["data"]))

        self._task_dispatcher_client.clear_task(task["type"], task["key"])
        logger.info(f"Task of type {task['type'].value} for key {task['key']} was completed!")

    async def _forward_ticket(self, ticket_id: int, serial_number: str, target_queue: str, **_kwargs):
        change_detail_work_queue_response = await self._bruin_repository.change_detail_work_queue(
            ticket_id, serial_number, target_queue
        )
        return change_detail_work_queue_response["status"] in range(200, 300)
