# Run Hawkeye Customer Cache Refresh job

```python
logger.info("Starting job to refresh the cache of hawkeye...")
```

```python
logger.info("Claiming all probes from Hawkeye...")
```

[HawkeyeRepository::get_probes](../../repositories/hawkeye_repository/get_probes.md)

* If no devices could be retrieved:
    ```python
    logger.error(f"Bad status calling get_probes. Error: {probes_response['status']}. Re-trying job...")
    ```
  
    * If the attempts' threshold to retry retrieving devices has not been maxed out yet:
      ```python
      logger.warning("Couldn't find any probe to refresh the cache. Re-trying job...")
      ```
      _The Hawkeye Customer Cache Refresh job triggers immediately again_
    * Otherwise:
      ```python
      error_message = (
          "[hawkeye-customer-cache] Too many consecutive failures happened while trying "
          "to claim the list of probes of hawkeye"
      )
      raise Exception(error_message)
      ...
      logger.error(f"An error occurred while refreshing the hawkeye cache -> {e}")
      ```
      END

```python
logger.info("Got all probes from Hawkeye!")
```

```python
logger.info(f"Got {len(probes_list)} probes from Hawkeye")
```

```python
logger.info("Refreshing cache for hawkeye")
```

* For each device:
    * If the device has never been contacted:
      ```python
      logger.warning(f"Device {device['serialNumber']} has never been contacted. Skipping...")
      ```
      _Continue with next device_

    [BruinRepository::filter_probe](../../repositories/bruin_repository/filter_probe.md)

```python
logger.info(f"Finished filtering probes for hawkeye")
```

```python
logger.info(f"Storing cache of {len(cache)} devices to Redis for hawkeye")
```

[StorageRepository::set_hawkeye_cache](../../repositories/storage_repository/set_hawkeye_cache.md)

[_send_email_multiple_inventories](_send_email_multiple_inventories.md)

```python
logger.info("Finished refreshing hawkeye cache!")
```