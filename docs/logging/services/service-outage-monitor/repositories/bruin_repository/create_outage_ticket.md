## Create Service Outage ticket for VeloCloud edge

```python
logger.info(f"Creating outage ticket for device {service_number} that belongs to client {client_id}...")
```

* If there's an error while asking for the data to the `bruin-bridge`:
  ```python
  err_msg = (
      f"An error occurred when creating outage ticket for device {service_number} belong to client"
      f"{client_id} -> {e}"
  )
  [...]
  logger.error(err_msg)
  ```
  END

```python
logger.info(f"Outage ticket for device {service_number} that belongs to client {client_id} created!")
```

* If response status for create outage ticket is not any of `200`, `409`, `471`, `472` or `473`:
  ```python
  err_msg = (
      f"Error while creating outage ticket for device {service_number} that belongs to client "
      f"{client_id} in {self._config.CURRENT_ENVIRONMENT.upper()} environment: "
      f"Error {response_status} - {response_body}"
  )
  [...]
  logger.error(err_msg)
  ```