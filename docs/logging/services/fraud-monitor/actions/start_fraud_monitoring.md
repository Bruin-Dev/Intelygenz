## Start fraud monitoring

```python
logger.info("Scheduling Fraud Monitor job...")
```
* If exec on start:
  ```python
  logger.info("Fraud Monitor job is going to be executed immediately")
  ```
* [_fraud_monitoring_process](_fraud_monitoring_process.md)
* If ConflictingIdError:
  ```python
  logger.info(f"Skipping start of Fraud Monitoring job. Reason: {conflict}")
  ```