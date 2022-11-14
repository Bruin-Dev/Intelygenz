## Schedule Service Outage Monitoring job
```python
logger.info("Scheduling Service Outage Monitor job...")
```

* If job should be executed on service start:
  ```python
  logger.info("Service Outage Monitor job is going to be executed immediately")
  ```

[_outage_monitoring_process](_outage_monitoring_process.md)

* If there's a running job to monitor Service Outage issues already:
  ```python
  logger.error(f"Skipping start of Service Outage Monitoring job. Reason: {conflict}")
  ```