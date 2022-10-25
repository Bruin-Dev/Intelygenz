## Subject: bruin.customer.get.info

_Message arrives at subject_

* If message doesn't have a body:
  ```python
  self._logger.error(f"Cannot get bruin client info using {json.dumps(msg)}. JSON malformed")
  ```
  END

* If message body doesn't have `service_number`:
  ```python
  self._logger.error(f'Cannot get bruin client info using {json.dumps(filters)}. Need "service_number"')
  ```
  END

```python
self._logger.info(f"Getting Bruin client ID with filters: {json.dumps(filters)}")
```

[get_client_info](../repositories/bruin_repository/get_client_info.md)

```python
self._logger.info(
            f"Bruin client_info published in event bus for request {json.dumps(msg)}. "
            f"Message published was {response}"
        )
```
