## Subject: bruin.get.asset.topics

_Message arrives at subject_

* If message body doesn't have `client_id` or `service_number`:
  ```python
  logger.error(f"Cannot get asset topics using {json.dumps(msg)}. " f"JSON malformed")
  ```
  END

_Try converting message body.client_id into an int_

* If `ValueError`  is caught:
  ```python
  logger.error(f"body.client_id {payload.get('client_id')} should be an int.")
  ```
  END

_Getting `service_number` from message body_

* If message body doesnt have a value for `service_number`:
  ```python
  logger.error(f"body.service_number can't be empty")
  ```
  END

```python
logger.info(f"Getting asset topics for client '{client_id}', service number '{service_number}'")
```

[get_asset_topics](../repositories/bruin_repository/get_asset_topics.md)
