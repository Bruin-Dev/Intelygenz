## Start intermapper outage monitoring
```
self._logger.info("Scheduling InterMapper Monitor job...")
```
* If exec on start:
  ```
  self._logger.info("InterMapper Monitor job is going to be executed immediately")
  ```
  * [_intermapper_monitoring_process](_intermapper_monitoring_process.md)
* If ConflictingIdError:
  ```
  self._logger.info(f"Skipping start of InterMapper Monitoring job. Reason: {conflict}")
  ```