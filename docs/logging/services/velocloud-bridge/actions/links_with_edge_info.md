## Subject: get.links.with.edge.info

_Message arrives at subject_

* If message doesn't have a body:
  ```python
  logger.error(f'Cannot get links with edge info: "body" is missing in the request')
  ```
  END

* If message body doesn't have `host` filter:
  ```python
  logger.error(f'Cannot get links with edge info: "host" is missing in the body of the request')
  ```
  END

```python
logger.info(f'Getting links with edge info from Velocloud host "{velocloud_host}"...')
```

[get_links_with_edge_info](../repositories/velocloud_repository/get_links_with_edge_info.md)

```python
logger.info(f"Response sent for request {payload}")
```