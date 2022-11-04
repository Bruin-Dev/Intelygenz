## Fetch Bruin data for an edge, and cross it with VeloCloud's

```python
logger.info(f"Checking if edge {serial_number} should be monitored...")
```

[BruinRepository::get_client_info](../../repositories/bruin_repository/get_client_info.md)

* If response status for get edge's client info in Bruin is not ok:
  ```python
  logger.error(f"Error while fetching client info for edge {serial_number}: {client_info_response}")
  ```
  END

* If the edge seems to be linked to multiple clients in Bruin:
  ```python
  logger.info(f"Edge {serial_number} has {len(client_info_response_body)} inventories in Bruin")
  ```
  _Edge will be reported as having multiple inventories at the end of the caching process_

* If the edge doesn't have any client info associated in Bruin:
  ```python
  logger.warning(f"Edge with serial {serial_number} doesn't have any Bruin client info associated")
  ```
  _Edge will be excluded from the cache right before saving it_

    END

[BruinRepository::get_management_status](../../repositories/bruin_repository/get_management_status.md)

* If response status for get edge's management status in Bruin is not ok:
  ```python
  logger.error(
      f"Error while fetching management status for edge {serial_number}: {management_status_response}"
  )
  ```
  END

* If edge's management status is not monitorable:
  ```python
  logger.warning(f"Management status is not active for {edge_identifier}. Skipping...")
  ```
  _Edge will be excluded from the cache right before saving it_
  
    END

* If edge's management status is `Pending` and its owner (client) is blacklisted from monitoring for such status:
  ```python
  logger.warning(
      f"Edge ({serial_number}) has management_status: Pending and has a blacklisted"
      f"client_id: {client_id}. Skipping..."
  )
  ```
  _Edge will be excluded from the cache right before saving it_
  
    END

```python
logger.info(f"Management status for {serial_number} seems active")
```

[BruinRepository::get_site_details](../../repositories/bruin_repository/get_site_details.md)

* If response status for get edge's site details in Bruin is not ok:
  ```python
  logger.error(f"Error while fetching site details for edge {serial_number}: {site_details_response}")
  ```
  END

_VeloCloud and Bruin data for the edge are finally crossed_

* If the whole crossing process fails for unexpected reasons:

    _Run the crossing process again_

* If the whole crossing process fails after multiple attempts:
  ```python
  logger.error(f"An error occurred while checking if edge {serial_number} should be cached or not -> {e}")
  ```