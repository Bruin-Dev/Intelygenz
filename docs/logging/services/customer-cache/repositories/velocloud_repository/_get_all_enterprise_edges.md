## Get all edges belonging to an enterprise in a VCO

```python
logger.info(f"Getting all edges from Velocloud host {host} and enterprise ID {enterprise_id}...")
```

* If there's an error while asking for the data to the `velocloud-bridge`:
  ```python
  err_msg = (
      f"An error occurred when requesting edge list from host {host} and enterprise "
      f"ID {enterprise_id} -> {e}"
  ) 
  [...]
  logger.error(err_msg)
  ```
  END

```python
logger.info(f"Got all edges from Velocloud host {host} and enterprise ID {enterprise_id}!")
```

* If response status for get all edges belonging to an enterprise is not ok:
  ```python
  err_msg = (
      f"Error while retrieving edge list in {self._config.ENVIRONMENT_NAME.upper()} "
      f"environment: Error {response_status} - {response_body}"
  )
  [...]
  logger.error(err_msg)
  ```