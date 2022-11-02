## Schedule Lumin Billing Report job
```python
logger.info("Scheduled task: billing report process configured to run first day of each month")
```

* If job should be executed on service start:
  ```python
  logger.info(f"It will be executed now")
  ```

[_billing_report_process](_billing_report_process.md)

* If the job cannot succeed:
  ```python
  logger.exception("Execution failed for billing report", event.exception)
  ```
  _The job is triggered again immediately_
