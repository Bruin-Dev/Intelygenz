import logging

logger = logging.getLogger(__name__)


class DRIRepository:
    def __init__(self, storage_repository, dri_client):
        self._storage_repository = storage_repository
        self._dri_client = dri_client

    async def get_dri_parameters(self, serial_number, parameter_set):
        task_id_response = await self._get_task_id(serial_number, parameter_set)
        if task_id_response["status"] not in range(200, 300):
            logger.error(
                f"An error occurred while getting a task ID for serial number {serial_number}: {task_id_response}"
            )
            return task_id_response

        task_id = task_id_response["body"]
        logger.info(f"Checking task_id status for the task_id {task_id} of serial_number {serial_number}")
        get_task_results_response = await self._get_task_results(serial_number, task_id)
        return get_task_results_response

    async def _get_task_id(self, serial_number, parameter_set):
        logger.info(f"Checking redis for task id from DRI for serial_number {serial_number}")

        task_id = self._storage_repository.get(serial_number)

        task_id_response = {"body": task_id, "status": 200}

        if task_id is None:
            logger.info(
                f"No task ids found from redis for serial_number {serial_number}. Checking "
                f"if any task_ids are currently in the pending task queue..."
            )

            pending_task_ids = await self._get_pending_task_ids(serial_number)
            if pending_task_ids["status"] not in range(200, 300):
                logger.error(
                    f"An error occurred while looking for pending tasks for serial number {serial_number}: "
                    f"{pending_task_ids}"
                )
                task_id_response["status"] = pending_task_ids["status"]
                task_id_response["body"] = pending_task_ids["body"]
                return task_id_response

            if len(pending_task_ids["body"]) > 0:
                logger.info(
                    f"Found {len(pending_task_ids['body'])} pending tasks for serial number {serial_number}: "
                    f"{pending_task_ids}"
                )
                task_id_response["status"] = pending_task_ids["status"]
                task_id_response["body"] = max(pending_task_ids["body"])
                self._storage_repository.save(serial_number, task_id_response["body"])

            if len(pending_task_ids["body"]) == 0:
                logger.info(
                    f"No task ids found from the pending task queue for serial_number {serial_number}. "
                    f"Getting task_id from DRI..."
                )
                task_id_response = await self._get_task_id_from_dri(serial_number, parameter_set)

        return task_id_response

    async def _get_task_id_from_dri(self, serial_number, parameter_set):
        task_id_response = await self._dri_client.get_task_id(serial_number, parameter_set)
        if task_id_response["status"] not in range(200, 300):
            logger.error(
                f"An error occurred when getting task_id from DRI for serial {serial_number}: {task_id_response}"
            )
            return task_id_response

        if task_id_response["body"]["status"] != "SUCCESS":
            logger.error(f"Getting task_id of {serial_number} failed. Response returned {task_id_response['body']}")
            task_id_response["status"] = 400
            return task_id_response

        dri_task_id = task_id_response["body"]["data"]["Id"]
        self._storage_repository.save(serial_number, dri_task_id)
        logger.info(f"Got task id {dri_task_id} from DRI for serial {serial_number}")
        return {"body": dri_task_id, "status": task_id_response["status"]}

    async def _get_task_results(self, serial_number, task_id):
        task_results_response = await self._dri_client.get_task_results(serial_number, task_id)

        if task_results_response["status"] == 401:
            logger.warning(
                f"Got authentication error from DRI while looking for results of task {task_id} for "
                f"serial number {serial_number}"
            )
            return task_results_response

        if task_results_response["status"] not in range(200, 300):
            logger.error(
                f"An error occurred while looking for results of task {task_id} for serial number "
                f"{serial_number}: {task_results_response}"
            )
            self._storage_repository.remove(serial_number)
            return task_results_response

        task_results = task_results_response["body"]

        if task_results["status"] != "SUCCESS":
            logger.error(
                f"Checking if task_id {task_id} of {serial_number} is complete failed. "
                f"Response returned {task_results}"
            )
            task_results_response["body"] = f"Failed to retrieve data from DRI for serial {serial_number}"
            task_results_response["status"] = 400
            self._storage_repository.remove(serial_number)
            return task_results_response

        if task_results["data"]["Message"] == "Pending":
            logger.info(f"Task {task_id} for serial number {serial_number} is still in progress")
            task_results_response["body"] = f"Data is still being fetched from DRI for serial {serial_number}"
            task_results_response["status"] = 204
            return task_results_response

        if task_results["data"]["Message"] == "Rejected":
            logger.warning(f"Task {task_id} for serial number {serial_number} was rejected")
            task_results_response["body"] = f"DRI task was rejected for serial {serial_number}"
            task_results_response["status"] = 403
            self._storage_repository.remove(serial_number)
            return task_results_response

        completed_task_data = {}
        for data in task_results["data"]["Parameters"]:
            completed_task_data[data["Name"]] = data["Value"]

        task_results_response["body"] = completed_task_data
        task_results_response["status"] = 200
        return task_results_response

    async def _get_pending_task_ids(self, serial_number):
        pending_task_ids_response = await self._dri_client.get_pending_task_ids(serial_number)

        if pending_task_ids_response["status"] not in range(200, 300):
            logger.error(f"Failed to get pending task ids list from DRI for serial {serial_number}")
            return pending_task_ids_response

        if pending_task_ids_response["body"]["status"] != "SUCCESS":
            logger.error(
                f"Getting list of pending tasks for serial {serial_number} failed."
                f"Response returned {pending_task_ids_response['body']}"
            )
            pending_task_ids_response["status"] = 400
            return pending_task_ids_response

        pending_task_ids = [task["Id"] for task in pending_task_ids_response["body"]["data"]["Transactions"]]
        logger.info(f"Pending task ids list from DRI for serial {serial_number} found: {pending_task_ids}")

        return {"body": pending_task_ids, "status": 200}
