## Subject: request.network.gateway.list

_Message arrives at subject_

* If message doesn't have the expected format:
  ```python
  logger.warning(f"Wrong request message: msg={msg}, validation_error={e}")
  ```
  END

```python
logger.info(f"Getting network gateway list on host {host}...")
```

[get_network_gateways](../repositories/velocloud_repository/get_network_gateways.md)

```python
logger.info(f"Sent network gateway list on host {host}")
```