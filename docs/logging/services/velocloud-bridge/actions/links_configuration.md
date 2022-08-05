## Subject: request.links.configuration

_Message arrives at subject_

* If message doesn't have a body:
  ```python
  logger.error(f"Cannot get links configuration with {json.dumps(payload)}. JSON malformed")
  ```
  END

* If message body doesn't have `edge`, `start_date`, or `end_date` filters:
  ```python
  logger.error(
      f'Cannot get links configuration with {json.dumps(payload)}. Need parameters "host", "enterprise_id" '
      f'and "edge_id"'
  )
  ```
  END

```python
logger.info(f"Getting links configuration for edge {edge_full_id}...")
```

[get_links_configuration](../repositories/velocloud_repository/get_links_configuration.md)

```python
logger.info(f"Published links configuration for edge {edge_full_id}")
```