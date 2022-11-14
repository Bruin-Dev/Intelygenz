## Schedule Triage job

```python
logger.info(
    f"Scheduled task: service outage triage configured to run every "
    f'{self._config.TRIAGE_CONFIG["polling_minutes"]} minutes'
)
```

* If job should be executed on service start:
  ```python
  logger.info(f"It will be executed now")
  ```

[_run_tickets_polling](_run_tickets_polling.md)