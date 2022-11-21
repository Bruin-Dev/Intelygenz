## Start tnba automated process (Start of service)
```
self._logger.info("Scheduling TNBA automated process job...")
```
* If exec on start:
  ```
  self._logger.info("TNBA automated process job is going to be executed immediately")
  ```
* [_run_tickets_polling](_run_tickets_polling.md)
* If ConflictingIdError:
  ```
  self._logger.info(f"Skipping start of TNBA automated process job. Reason: {conflict}")
  ```