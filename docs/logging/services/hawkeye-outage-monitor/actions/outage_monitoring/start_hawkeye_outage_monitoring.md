## Schedule Hawkeye Outage Monitoring job
```python
logger.info("Scheduling Hawkeye Outage Monitor job...")
```

* If job should be executed on service start:
  ```python
  logger.info("Hawkeye Outage Monitor job is going to be executed immediately")
  ```

[_outage_monitoring_process](_outage_monitoring_process.md)

* If there's a running job to monitor Ixia devices already:
  ```python
  logger.warning(f"Skipping start of Hawkeye Outage Monitoring job. Reason: {conflict}")
  ```