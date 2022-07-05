## Start service outage monitoring (**start the process of outage**)
```
self._logger.info("Scheduling Service Outage Monitor job...")
```
* If exe on start:
  ```
  self._logger.info("Service Outage Monitor job is going to be executed immediately")
  ```
* [_outage_monitoring_process](_outage_monitoring_process.md)
* If Exception:
  ```
  self._logger.error(f"Skipping start of Service Outage Monitoring job. Reason: {conflict}")
  ```