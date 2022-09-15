## Get network gateway list

```python
self._logger.info(f"Getting network gateway list from Velocloud host {velocloud_host}...")
```

* If there's an exception:
    ```python
    self._logger.error(f"An error occurred when requesting network gateway list from Velocloud -> {e}")
    ```

* If response status is not OK:
    ```python
    self._logger.error(
      f"Error while retrieving network gateway list from Velocloud in {environment} "
      f"environment: Error {response_status} - {response_body}"
    )
    ```
* Else:
    ```python
    self._logger.info(f"Got network gateway list from Velocloud host {velocloud_host}!")
    ```
