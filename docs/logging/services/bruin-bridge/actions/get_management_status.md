## Subject: bruin.inventory.management.status

_Message arrives at subject_

* If message doesn't have a body:
  ```python
  logger.error(f"Cannot get management status using {json.dumps(msg)}. JSON malformed")
  ```
  END

* If message body doesn't have `client_id`, `status`, or `service_number`:
  ```python
  logger.info(
                f"Cannot get management status using {json.dumps(filters)}. "
                f'Need "client_id", "status", "service_number"'
            )
  ```
  END

```python
logger.info(f"Getting management status with filters: {json.dumps(filters)}")
```

[get_management_status](../repositories/bruin_repository/get_management_status.md)

```python
logger.info(
            f"Management status published in event bus for request {json.dumps(msg)}. "
            f"Message published was {response}"
        )
```
