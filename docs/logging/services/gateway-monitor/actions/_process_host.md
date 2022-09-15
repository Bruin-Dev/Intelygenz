## Process host

```python
self._logger.info(f"Processing Velocloud host {host}...")
```

* For each gateway in the host:
    * If there's an exception getting gateway metrics:
        ```python
        self._logger.exception(e)
        ```

[_get_unhealthy_gateways](_get_unhealthy_gateways.md)

* If there are any unhealthy gateways:
    ```python
    self._logger.info(f"{len(unhealthy_gateways)} unhealthy gateway(s) found for host {host}")
    ```
    * For each unhealthy gateway:
        * [_report_servicenow_incident](_report_servicenow_incident.md)
        * If there's an exception:
            ```python
            self._logger.exception(e)
            ```
* Else:
    ```python
    self._logger.info(f"No unhealthy gateways were found for host {host}")
    ```

```python
self._logger.info(f"Finished processing Velocloud host {host}!")
```
