## Subject: request.edge.links.series

_Message arrives at subject_

* If message doesn't have a body:
  ```python
  logger.error(f"Cannot get edge links series with {json.dumps(payload)}. JSON malformed")
  ```
  END

* If message body doesn't have the appropriate shape:
  ```python
  logger.error(
      f"Cannot get edge links series with {json.dumps(payload)}. Make sure it complies with the shape of "
      f"{REQUEST_MODEL}"
  )
  ```
  END

* If body's `payload` doesn't have any filter of `enterpriseId`, `edgeId`, `interval` and `metrics`:
  ```python
  logger.error(
      f'Cannot get edge links series with {json.dumps(payload)}. Need parameters "enterpriseId", "edgeId", '
      f'"interval" and "metrics" under "payload"'
  )
  ```
  END

```python
logger.info(f"Getting edge links series from host {host} using payload {payload}...")
```

[get_edge_links_series](../repositories/velocloud_repository/get_edge_links_series.md)

```python
logger.info(f"Published edge links series for host {host} and payload {payload}")
```