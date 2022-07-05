## Start hawkeye outage monitoring (Start of service)
```
self._logger.info("Scheduling Hawkeye Outage Monitor job...")
```
* If exec on start:
  ```
  self._logger.info("Hawkeye Outage Monitor job is going to be executed immediately")
  ```
* If ConflictingIdError:
  ```
  self._logger.info(f"Skipping start of Hawkeye Outage Monitoring job. Reason: {conflict}")
  ```