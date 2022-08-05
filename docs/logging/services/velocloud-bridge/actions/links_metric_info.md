## Subject: get.links.metric.info

_Message arrives at subject_

* If message doesn't have a body:
  ```python
  logger.error(f'Cannot get links metric info: "body" is missing in the request')
  ```
  END

* If message body doesn't have `host` filter:
  ```python
  logger.error(f'Cannot get links metric info: "host" is missing in the body of the request')
  ```
  END

* If message body doesn't have `interval` filter:
  ```python
  logger.error(f'Cannot get links metric info: "interval" is missing in the body of the request')
  ```
  END

```python
logger.info(f'Getting links metric info from Velocloud host "{velocloud_host}"...')
```

[get_links_metric_info](../repositories/velocloud_repository/get_links_metric_info.md)

```python
logger.info(f"Published links metric info for request {payload}")
```