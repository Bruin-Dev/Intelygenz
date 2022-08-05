## Subject: request.gateway.status.metrics

_Message arrives at subject_

* If message doesn't have the expected format:
  ```python
  logger.warning(f"Wrong request message: msg={msg}, validation_error={e}")
  ```
  END

```python
logger.info(f"Getting gateway status metrics for gateway {gateway_id} on host {host} in interval {interval}...")
```

[get_gateway_status_metrics](../repositories/velocloud_repository/get_gateway_status_metrics.md)

```python
logger.info(f"Sent gateway status metrics for gateway {gateway_id} on host {host} in interval {interval}")
```