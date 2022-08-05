## Subject: request.enterprises.edges

_Message arrives at subject_

* If message doesn't have a body:
  ```python
  logger.error(f"Cannot get enterprise edges with {json.dumps(payload)}. JSON malformed")
  ```
  END

* If message body doesn't have `edge`, `start_date`, or `end_date` filters:
  ```python
  logger.error(
      f'Cannot get edge events with {json.dumps(payload)}. Need parameters "edge", "start_date" and "end_date"'
  )
  ```
  END

```python
logger.info(f"Getting edges for host {host} and enterprise {enterprise_id}...")
```

[get_enterprise_edges](../repositories/velocloud_repository/get_enterprise_edges.md)

```python
logger.info(f"Sent list of enterprise edges for enterprise {enterprise_id} and host {host}")
```