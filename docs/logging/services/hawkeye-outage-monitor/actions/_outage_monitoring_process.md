## Outage monitoring process
```
self._logger.info(f"Starting Hawkeye Outage Monitor!")
```
* [get_cache_for_outage_monitoring](../repositories/customer_cache_repository/get_cache_for_outage_monitoring.md)
* If status is not ok:
  ```
  self._logger.warning(f"Bad status calling to get cache. Skipping hawkeyey outage monitoring process ...")
  ```
* [get_probes](../repositories/hawkeye_repository/get_probes.md)
* If status is not ok:
  ```
  self._logger.warning(f"Bad status calling to get probes. Skipping hawkeye outage monitoring process ...")
  ```
* If not probes:
  ```
  self._logger.info("The list of probes arrived empty. Skipping monitoring process...")
  ```
* If not active probes:
  ```
  self._logger.info("All probes were detected as inactive. Skipping monitoring process...")
  ```
* [_map_probes_info_with_customer_cache](_map_probes_info_with_customer_cache.md)
* If outage devices:
  ```
  self._logger.info(
                f"{len(outage_devices)} devices were detected in outage state. "
                "Scheduling re-check job for all of them..."
            )
  ```
  * [_schedule_recheck_job_for_devices](_schedule_recheck_job_for_devices.md)
* Else:
  ```
  self._logger.info("No devices were detected in outage state. Re-check job won't be scheduled")
  ``` 
* If healthy edges:
  ```
  self._logger.info(
                f"{len(healthy_devices)} devices were detected in healthy state. Running autoresolve for all of them"
            )
  ```
  * [_run_ticket_autoresolve](_run_ticket_autoresolve.md)
* Else:
  ```
  self._logger.info("No devices were detected in healthy state. Autoresolve won't be triggered")
  ```
```
self._logger.info(f"Hawkeye Outage Monitor process finished! Took {round((stop - start) / 60, 2)} minutes")
```