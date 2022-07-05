## Start triage job (star process of triage)
```
self._logger.info(
            f"Scheduled task: service outage triage configured to run every "
            f'{self._config.TRIAGE_CONFIG["polling_minutes"]} minutes'
        )
```
* If exec on start:
  ```
  self._logger.info(f"It will be executed now")
  ```
* [_run_tickets_polling](_run_tickets_polling.md)