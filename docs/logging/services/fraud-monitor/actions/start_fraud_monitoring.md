## Start fraud monitoring
```
self._logger.info("Scheduling Fraud Monitor job...")
```
* If exec on start:
  ```
  self._logger.info("Fraud Monitor job is going to be executed immediately")
  ```
* [_fraud_monitoring_process](_fraud_monitoring_process.md)
* If ConflictingIdError:
  ```
  self._logger.info(f"Skipping start of Fraud Monitoring job. Reason: {conflict}")
  ```