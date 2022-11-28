## Process host

```python
logger.info(f"Processing Velocloud host {host}...")
```

* For each gateway in the host:

    [VelocloudRepository::get_network_gateway_list](../repositories/velocloud_repository/get_network_gateway_list.md)

    * If there's an exception getting gateway metrics:
        ```python
        logger.exception(e)
        ```

[_get_unhealthy_gateways](_get_unhealthy_gateways.md)

* If there are any unhealthy gateways:
    ```python
    logger.info(f"{len(unhealthy_gateways)} unhealthy gateway(s) found for host {host}")
    ```
    * For each unhealthy gateway:

        [_report_servicenow_incident](_report_servicenow_incident.md)

        * If there's an exception:
          ```python
          logger.exception(e)
          ```
* Else:
    ```python
    logger.info(f"No unhealthy gateways were found for host {host}")
    ```

```python
logger.info(f"Finished processing Velocloud host {host}!")
```
