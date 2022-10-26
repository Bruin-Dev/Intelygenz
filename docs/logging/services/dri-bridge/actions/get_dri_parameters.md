## Subject: dri.parameters.request

_Message arrives at subject_

* If message doesn't have `body`:
  ```python
  logger.error(f"Cannot get DRI parameters using {json.dumps(payload)}. JSON malformed")
  ```
  END

* If message body doesn't have `serial_number` and `parameter_set` filters:
  ```python
  logger.error(f'Cannot get DRI parameters using {json.dumps(params)}. Need "serial_number" and ' f'"parameter_set"')
  ```
  END

```python
logger.info(f"Getting DRI parameters for serial_number {serial_number}")
```

[DRIRepository::get_dri_parameters](../repositories/dri_repository/get_dri_parameters.md)

```python
logger.info(
    f"The DRI parameters response for serial {serial_number} was published in "
    f"event bus for request {json.dumps(payload)}. "
    f"Message published was {response}"
)
```
