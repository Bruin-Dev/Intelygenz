## Get task results for serial number

[DRIClient::get_task_results](../../clients/dri_client/get_task_results.md)

* If an authentication error took place while fetching the results of a task linked to the serial number from DRI:
  ```python
  logger.warning(
      f"Got authentication error from DRI while looking for results of task {task_id} for "
      f"serial number {serial_number}"
  )
  ```
  END

* If some other error took place:
  ```python
  logger.error(
      f"An error occurred while looking for results of task {task_id} for serial number "
      f"{serial_number}: {task_results_response}"
  )
  ```
  _Task ID linked to the serial number is removed from Redis_

    END

* If DRI returned a response but the request couldn't succeed on their system:
  ```python
  logger.error(
      f"Checking if task_id {task_id} of {serial_number} is complete failed. "
      f"Response returned {task_results}"
  )
  ```
  _Task ID linked to the serial number is removed from Redis_

    END

* If DRI reported that the task linked to the serial number is still in progress:
  ```python
  logger.info(f"Task {task_id} for serial number {serial_number} is still in progress")
  ```

    END

* If DRI reported that the task linked to the serial number was rejected:
  ```python
  logger.warning(f"Task {task_id} for serial number {serial_number} was rejected")
  ```

    END
