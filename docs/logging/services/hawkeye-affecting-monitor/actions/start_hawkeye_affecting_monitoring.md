## Start hawkeye affecting monitoring (Start service)
```
self._logger.info("Scheduling Hawkeye Affecting Monitor job...")
```
* If exec on start:
  ```
  self._logger.info("Hawkeye Affecting Monitor job is going to be executed immediately")
  ```
* [_affecting_monitoring_process](_affecting_monitoring_process.md)
* If ConflictingIdError:
  ```
  self._logger.info(f"Skipping start of Hawkeye Affecting Monitoring job. Reason: {conflict}") 
  ```