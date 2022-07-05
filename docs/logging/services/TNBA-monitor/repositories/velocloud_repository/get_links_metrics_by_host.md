## Get links metrics by host

```
self._logger.info(
                f"Getting links metrics between {interval['start']} and {interval['end']} "
                f"from Velocloud host {host}..."
            )
```

* If `Exception`

  ```
  f"An error occurred when requesting links metrics from Velocloud -> {e}"
  ```

```
self._logger.info(f"Got links metrics from Velocloud host {host}!")
```

* Else:

  ```
  self._logger.error(f"Error while retrieving links metrics in {self._config.ENVIRONMENT_NAME.upper()} "
                     f"environment: Error {response_status} - {response_body}")
  ```
