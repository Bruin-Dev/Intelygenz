## Get DRI parameters

[_get_task_id](_get_task_id.md)

* If an error took place while looking for a task ID linked to the serial number:
  ```python
  logger.error(
      f"An error occurred while getting a task ID for serial number {serial_number}: {task_id_response}"
  )
  ```
  END

```python
logger.info(f"Checking task_id status for the task_id {task_id} of serial_number {serial_number}")
```

[_get_task_results](_get_task_results.md)