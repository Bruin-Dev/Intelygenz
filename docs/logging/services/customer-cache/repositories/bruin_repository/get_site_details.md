## Get site details for edge

```python
logger.info(f"Getting site details of site {site_id} and client {client_id}...")
```

* If there's an error while asking for the data to the `bruin-bridge`:
  ```python
  err_msg = f"An error occurred while getting site details of site {site_id} and client {client_id}... -> {e}"
  [...]
  logger.error(err_msg)
  ```
  END

* If response status for get site details for edge is ok:
  ```python
  logger.info(f"Got site details of site {site_id} and client {client_id} successfully!")
  ```
* Otherwise:
  ```python
  err_msg = (
      f"Error while getting site details of site {site_id} and client {client_id} in "
      f"{self._config.ENVIRONMENT_NAME.upper()} environment: Error {response_status} - {response_body}"
  )
  [...]
  logger.error(err_msg)
  ```