## Get ticket basic info
```python
self._logger.info(
    f"Getting all tickets basic info with any status of {ticket_statuses}, with ticket topic "
    f"VOO, service number {service_number} and belonging to client {client_id} from Bruin..."
)
```

* If there's an error while asking for the data to the `bruin-bridge`:
  ```python
  err_msg = (
      f"An error occurred when requesting tickets  basic info from Bruin API with any status"
      f" of {ticket_statuses}, with ticket topic VOO and belonging to client {client_id} -> {e}"
  )
  [...]
  self._logger.error(err_msg)
  ```
  END

* If response status for get ticket basic info is not ok:
  ```python
  err_msg = (
      f"Error while retrieving tickets basic info with any status of {ticket_statuses}, "
      f"with ticket topic VOO, service number {service_number} and belonging to client {client_id} in "
      f"{self._config.ENVIRONMENT_NAME.upper()} environment: "
      f"Error {response_status} - {response_body}"
  )
  [...]
  self._logger.error(err_msg)
  ```
* Otherwise:
  ```python
  self._logger.info(
      f"Got all tickets basic info with any status of {ticket_statuses}, with ticket topic "
      f"VOO, service number {service_number} and belonging to client "
      f"{client_id} from Bruin!"
  )
  ```