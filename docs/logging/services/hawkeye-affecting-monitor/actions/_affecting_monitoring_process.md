## Affecting monitoring process
```
self._logger.info(f"Starting Hawkeye Affecting Monitor!")
```
* [get_cache_for_affecting_monitoring](../repositories/customer_cache_repository/get_cache_for_affecting_monitoring.md)
* If status is not Ok:
  ```
   self._logger.warning(f"Bad status calling to get cache. Skipping hawkeye affecting monitor process ...")
  ```
* [get_tests_results_for_affecting_monitoring](../repositories/hawkeye_repository/get_tests_results_for_affecting_monitoring.md)
* If status is not Ok:
  ```
  self._logger.warning(f"Bad request get test results for affectin monitor for probe uids: {probe_uids}."
                                 f"Skipping hawkeye affecting monitor ...")
  ```
```
self._logger.info(
            f"Looking for Service Affecting tickets for {len(cached_devices_mapped_to_tests_results)} devices..."
        )
```
* [_add_device_to_tickets_mapping](_add_device_to_tickets_mapping.md)
```
self._logger.info(f"Processing {len(cached_devices_mapped_to_tests_results)} devices...")
```
* [_process_device](_process_device.md)
```
self._logger.info(f"Hawkeye Affecting Monitor process finished! Took {round((stop - start) / 60, 2)} minutes")
```