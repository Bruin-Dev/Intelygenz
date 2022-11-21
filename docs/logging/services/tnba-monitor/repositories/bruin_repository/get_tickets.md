## Get ticket
```
self._logger.info(f'Getting all tickets with parameters of {request["body"]} from Bruin...')
```
* If Exception:
  ```
  self._logger.error(f'An error occurred when requesting tickets from Bruin API with parameters of {request["body"]} -> {e}')
  ```
* If status ok:
  ```
  self._logger.info(f'Got all tickets with parameters of {request["body"]} from Bruin!')
  ```
* Else:
  ```
  self._logger.error(f'Error while retrieving tickets with parameters of {request["body"]} in '
                     f"{self._config.CURRENT_ENVIRONMENT.upper()} environment: "
                     f"Error {response_status} - {response_body}")
  ```