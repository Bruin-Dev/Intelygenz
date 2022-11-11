## Create fraud ticket

```python
logger.info(
    f"Creating fraud ticket for service number {service_number} that belongs to client {client_id}..."
)
```
* If Exception:
  ```python
  logger.error(
      f"An error occurred when creating fraud ticket for service number {service_number} "
      f"that belongs to client {client_id} -> {e}"
  )
  ```
* If status ok:
  ```python
  logger.info(f"Fraud ticket for service number {service_number} that belongs to client {client_id} created!")
  ```
* Else:
  ```python
  logger.error(
      f"Error while creating fraud ticket for service number {service_number} that belongs to client "
      f"{client_id} in {self._config.ENVIRONMENT_NAME.upper()} environment: "
      f"Error {response_status} - {response_body}"
  )
  ```