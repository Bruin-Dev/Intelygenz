## Get gateway status metrics

```python
logger.info(
    f"Getting gateway status metrics from Velocloud host {gateway['host']} "
    f"for gateway {gateway['id']} for the past {lookup_interval // 60} minutes..."
)
```

* If there's an exception:
    ```python
    logger.error(f"An error occurred when requesting gateway status metrics from Velocloud -> {e}")
    ```

* If response status is not OK:
    ```python
    logger.error(
      f"Error while retrieving gateway status metrics from Velocloud in {environment} "
      f"environment: Error {response_status} - {response_body}"
    )
    ```
* Else:
    ```python
    logger.info(
      f"Got gateway status metrics from Velocloud host {gateway['host']} "
      f"for gateway {gateway['id']} for the past {lookup_interval // 60} minutes!"
    )
    ```
