## Get ticket

```python
logger.info(f'Getting all tickets with parameters of {request["body"]} from Bruin...')
```
* If Exception:
  ```python
  logger.error(f'An error occurred when requesting tickets from Bruin API with parameters of {request["body"]} -> {e}')
  ```
* If status ok:
  ```python
  logger.info(f'Got all tickets with parameters of {request["body"]} from Bruin!')
  ```
* Else:
  ```python
  logger.error(
      f'Error while retrieving tickets with parameters of {request["body"]} in '
      f"{self._config.CURRENT_ENVIRONMENT.upper()} environment: "
      f"Error {response_status} - {response_body}"
  )
  ```