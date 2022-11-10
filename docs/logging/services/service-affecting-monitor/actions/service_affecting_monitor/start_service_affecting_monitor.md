## Schedule Service Affecting Monitoring job
```python
logger.info("Scheduling Service Affecting Monitor job...")
```

* If job should be executed on service start:
  ```python
  logger.info("Service Affecting Monitor job is going to be executed immediately")
  ```

[_service_affecting_monitor_process](_service_affecting_monitor_process.md)

* If there's a running job to monitor Service Affecting trouble already:
  ```python
  logger.error(f"Skipping start of Service Affecting Monitoring job. Reason: {conflict}")
  ```
