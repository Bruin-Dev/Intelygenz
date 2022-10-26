## Create new task in DRI for serial number

[DRIClient::get_task_id](../../clients/dri_client/get_task_id.md)

* If an error took place while creating a new task in DRI for the serial number:
  ```python
  logger.error(
      f"An error occurred when getting task_id from DRI for serial {serial_number}: {task_id_response}"
  )
  ```
  END

* If DRI returned a response but the request couldn't succeed on their system:
  ```python
  logger.error(f"Getting task_id of {serial_number} failed. Response returned {task_id_response['body']}")
  ```
  END

_Task ID is linked to the serial number in Redis_

```python
logger.info(f"Got task id {dri_task_id} from DRI for serial {serial_number}")
```