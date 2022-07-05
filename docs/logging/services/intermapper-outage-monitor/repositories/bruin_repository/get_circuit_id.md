## Get circuit id
```
self._logger.info(f"Getting the translation of circuit_id {circuit_id}")
```
* If Exception:
  ```
  self._logger.error(f"Getting the translation of circuit_id {circuit_id} Error: {e}")
  ```
* If status not Ok:
  ```
  self._logger.error(f"Getting the translation of circuit_id {circuit_id} in "
                    f"{self._config.ENVIRONMENT_NAME.upper()} environment. Error: "
                    f"Error {response_status} - {response_body}")
  ```