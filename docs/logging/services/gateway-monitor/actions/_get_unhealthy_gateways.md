## Get unhealthy gateways

* For each gateway:
    * If the gateway doesn't have metrics:
        ```python
        self._logger.warning(f"Gateway {gateway['name']} from host {gateway['host']} has missing metrics")
        ```
