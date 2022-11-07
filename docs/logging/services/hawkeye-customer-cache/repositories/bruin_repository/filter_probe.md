## Fetch Bruin data for a device, and cross it with Ixia's

```python
logger.info(f"Checking if device with serial {serial_number} should be monitored...")
```

[BruinRepository::get_client_info](../../repositories/bruin_repository/get_client_info.md)

* If response status for get device's client info in Bruin is not ok:
  ```python
  logger.error(f"Error while fetching client info for device {serial_number}: {client_info_response}")
  ```
  END

* If the device seems to be linked to multiple clients in Bruin:
  ```python
  logger.info(f"Device {serial_number} has {len(client_info_response_body)} inventories in Bruin")
  ```
  _Device will be reported as having multiple inventories at the end of the caching process_

* If the device doesn't have any client info associated in Bruin:
  ```python
  logger.warning(f"Device with serial {serial_number} doesn't have any Bruin client info associated")
  ```
  END

[BruinRepository::get_management_status](../../repositories/bruin_repository/get_management_status.md)

* If response status for get device's management status in Bruin is not ok:
  ```python
  logger.error(
      f"Error while fetching management status for device {serial_number}: "
      f"{management_status_response}"
  )
  ```
  END

* If device's management status is not monitorable:
  ```python
  logger.warning(f"Management status is not active for serial {serial_number}. Skipping...")
  ```
  END

```python
logger.info(f"Management status for serial {serial_number} seems active")
```

_Ixia and Bruin data for the device are finally crossed_

* If the whole crossing process fails for unexpected reasons:

    _Run the crossing process again_

* If the whole crossing process fails after multiple attempts:
  ```python
  logger.error(f"An error occurred while checking if probe {probe['probeId']} should be cached or not -> {e}")
  ```