## Get task ID for serial number

```python
logger.info(f"Checking redis for task id from DRI for serial_number {serial_number}")
```

* If no task ID linked to the serial number was found:
  ```python
  logger.info(
      f"No task ids found from redis for serial_number {serial_number}. Checking "
      f"if any task_ids are currently in the pending task queue..."
  )
  ```
  [_get_pending_task_ids](_get_pending_task_ids.md)

    * If an error took place while looking for pending tasks linked to the serial number:
      ```python
      logger.error(
          f"An error occurred while looking for pending tasks for serial number {serial_number}: "
          f"{pending_task_ids}"
      )
      ```
      END

    * If pending tasks were found for serial number:
      ```python
      logger.info(
          f"Found {len(pending_task_ids['body'])} pending tasks for serial number {serial_number}: "
          f"{pending_task_ids}"
      )
      ```
      _Most recent task ID is linked to the serial number in Redis_
    * Otherwise:
      ```python
      logger.info(
          f"No task ids found from the pending task queue for serial_number {serial_number}. "
          f"Getting task_id from DRI..."
      )
      ```
      [_get_task_id_from_dri](_get_task_id_from_dri.md)
