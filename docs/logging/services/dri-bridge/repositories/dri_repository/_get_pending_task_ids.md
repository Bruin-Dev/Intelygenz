## Get pending tasks for serial number

[DRIClient::get_pending_task_ids](../../clients/dri_client/get_pending_task_ids.md)

* If an error took place while looking for pending tasks linked to the serial number:
  ```python
  logger.error(f"Failed to get pending task ids list from DRI for serial {serial_number}")
  ```
  END

* If DRI returned a response but the request couldn't succeed on their system:
  ```python
  logger.error(
      f"Getting list of pending tasks for serial {serial_number} failed."
      f"Response returned {pending_task_ids_response['body']}"
  )
  ```
  END

```python
logger.info(f"Pending task ids list from DRI for serial {serial_number} found: {pending_task_ids}")
```