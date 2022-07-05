## Map probes info with customer cache
* for probe in probes:
  * If not cached info:
    ```
    self._logger.info(f"No cached info was found for device {serial_number}. Skipping...")
    ```