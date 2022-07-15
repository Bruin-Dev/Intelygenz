## Get serial attribute from inventory

```python
self._logger.info(
    f"Getting inventory attributes' serial number for service number {service_number} and client ID"
    f" {client_id}"
)
```

* If there's an error while asking for the data to the `bruin-bridge`:
  ```python
  err_msg = (
      f"Error while getting inventory attributes' serial number for service number {service_number} and "
      f"client ID {client_id}: {e}"
  )
  [...]
  self._logger.error(err_msg)
  ```
  END

* If response status for get serial attribute from inventory is not ok:
  ```python
  err_msg = (
      f"Error while getting inventory attributes' serial number for service number {service_number} and "
      f"client ID {client_id} in {self._config.ENVIRONMENT_NAME.upper()} environment. Error: "
      f"Error {response_status} - {response_body}"
  )
  [...]
  self._logger.error(err_msg)
  ```
* Otherwise:
  ```python
  self._logger.info(
      f"Got inventory attributes' serial number for service number {service_number} and client ID "
      f"{client_id}"
  )
  ```