## Subject: request.network.enterprise.edges

_Message arrives at subject_

* If message doesn't have a body:
  ```python
  logger.error(f"Cannot get network enterprise edge list with {json.dumps(payload)}. JSON malformed")
  ```
  END

* If message body doesn't have `host` and `enterprise_ids` filters:
  ```python
  logger.error(
      f'Cannot get network enterprise edge list with {json.dumps(payload)}. Need parameters "host" and '
      f'"enterprise_ids"'
  )
  ```
  END

```python
logger.info(f"Getting network enterprise edge list for host {host} and enterprises {enterprise_ids}")
```

[get_network_enterprise_edges](../repositories/velocloud_repository/get_network_enterprise_edges.md)

```python
logger.info(f"Sent list of network enterprises edges for enterprises: {enterprise_ids} and host {host}")
```