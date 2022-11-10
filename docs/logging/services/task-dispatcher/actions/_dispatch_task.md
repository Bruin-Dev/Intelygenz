## Dispatch Task

```python
 logger.info(f"Dispatching task of type {task['type'].value} for key {task['key']}...")
```
[_forward_ticket](_forward_ticket.md)

* If the task succeeds:
    ```python
    logger.info(f"Task of type {task['type'].value} for key {task['key']} was completed!")
    ```
  
    [_publish_result](_publish_result.md)
  
    END

* If the task did not succeed and its TTL has not been reached yet:
  ```python
  logger.error(f"Task of type {task['type'].value} for key {task['key']} failed, retrying on the next run")
  ```
* otherwise

    [clear_task](task_dispatcher_client/clear_task.md)
    ```python
    logger.error(
      f"Task of type {task['type'].value} for key {task['key']} could not be completed "
      f"after {self._config.DISPATCH_CONFIG['ttl'] // 60 // 60} hours"
    )
    ```
    [_publish_result](_publish_result.md)
