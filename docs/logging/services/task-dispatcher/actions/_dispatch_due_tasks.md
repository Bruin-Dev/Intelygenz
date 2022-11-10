## Run Task Dispatcher job

```python
logger.info("Getting due tasks...")
```

The Task Dispatcher is called every minute, and starts off by getting all the due tasks.
It then takes all the data from those tasks and try to forward them one by one.
Finally, it publishes the results to NATS.

[get_due_tasks](task_dispatcher_client/get_due_tasks.md)

* If not tasks are found:
  ```python
  logger.info("No due tasks were found")
  ```
  END
* else:
    ```python
    logger.info(f"{len(due_tasks)} due task(s) found")
    ```

    * For each due task: 

        [_dispatch_task](_dispatch_task.md)

```python
logger.info("Finished dispatching due tasks!")
```
