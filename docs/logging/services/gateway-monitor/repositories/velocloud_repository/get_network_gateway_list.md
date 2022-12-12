## Get network gateway list

```python
logger.info(f"Getting network gateway list from Velocloud host {velocloud_host}...")
```

* If there's an exception:
    ```python
    logger.error(f"An error occurred when requesting network gateway list from Velocloud -> {e}")
    ```

* If response status is not OK:
    ```python
    logger.error(
      f"Error while retrieving network gateway list from Velocloud in {environment} "
      f"environment: Error {response_status} - {response_body}"
    )
    ```
* Else:
    ```python
    logger.info(f"Got network gateway list from Velocloud host {velocloud_host}!")
    ```
