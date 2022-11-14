## Get tickets

```python
logger.info(f'Getting all tickets with parameters of {request["body"]} from Bruin...')
```

* If there's an error while asking for the data to the `bruin-bridge`:
  ```python
  err_msg = (
      f'An error occurred when requesting tickets from Bruin API with parameters of {request["body"]} -> {e}'
  )
  [...]
  logger.error(err_msg)
  ```
  END

* If response status for get tickets is ok:
  ```python
  logger.info(f'Got all tickets with parameters of {request["body"]} from Bruin!')
  ```
* Otherwise:
  ```python
  err_msg = (
      f'Error while retrieving tickets with parameters of {request["body"]} in '
      f"{self._config.CURRENT_ENVIRONMENT.upper()} environment: "
      f"Error {response_status} - {response_body}"
  )
  [...]
  logger.error(err_msg)
  ```