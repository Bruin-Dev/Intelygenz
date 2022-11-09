## Schedule connect to all hosts

```python
logger.info(f"Scheduling job to connect to all hosts...")
```

[_connect_to_all_hosts](_connect_to_all_hosts.md) is scheduled to trigger immediately and then periodically

* If that job had already been scheduled:
    ```python
    logger.error(f"Skipping start of job to connect to all hosts. Reason: {conflict}")
    ```
* Otherwise:
    ```python
    logger.info(f"Job to connect to all hosts has been scheduled")
    ```