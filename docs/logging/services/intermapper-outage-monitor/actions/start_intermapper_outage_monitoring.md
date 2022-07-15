## Start InterMapper Outage Monitoring
```python
self._logger.info("Scheduling InterMapper Monitor job...")
```

* If job should be executed on service start:
  ```python
  self._logger.info("InterMapper Monitor job is going to be executed immediately")
  ```
  [_intermapper_monitoring_process](_intermapper_monitoring_process.md)

* If there's a running job to monitor InterMapper events already:
  ```python
  self._logger.info(f"Skipping start of InterMapper Monitoring job. Reason: {conflict}")
  ```
