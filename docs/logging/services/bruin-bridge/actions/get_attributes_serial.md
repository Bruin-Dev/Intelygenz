## Subject: bruin.inventory.attributes.serial

_Message arrives at subject_

* If message doesn't have a body:
  ```python
  self._logger.error(f"Cannot get attribute's serial number using {json.dumps(msg)}. JSON malformed")
  ```
  END

* If message body doesn't have `client_id`, `status` or `service_number`:
  ```python
  self._logger.info(
                f"Cannot get attribute's serial number using {json.dumps(filters)}. "
                f'Need "client_id", "status", "service_number"'
            )
  ```
  END

```python
self._logger.info(f"'Getting attribute's serial number with filters: {json.dumps(filters)}'")
```

[get_attributes_serial](../repositories/bruin_repository/get_attributes_serial.md)

```python
self._logger.info(
            f"'Attribute's serial number published in event bus for request {json.dumps(msg)}. '"
            f"Message published was {response}"
        )
```
