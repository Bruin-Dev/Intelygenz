## Get unhealthy gateways

* For each gateway:
    * If the gateway doesn't have metrics:
        ```python
        logger.warning(f"Gateway {gateway['name']} from host {gateway['host']} has missing metrics")
        ```
