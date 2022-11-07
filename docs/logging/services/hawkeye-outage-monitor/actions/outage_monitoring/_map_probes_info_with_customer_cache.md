## Map Ixia devices' current state to their info stored in the cache

* For each Ixia device:
    * If the Ixia device is not present in the cache of customers:
      ```python
      logger.warning(f"No cached info was found for device {serial_number}. Skipping...")
      ```
      _Continue with next device_