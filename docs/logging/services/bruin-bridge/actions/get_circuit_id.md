## Subject: bruin.get.circuit.id

_Message arrives at subject_

* If message doesn't have a body:
  ```python
  logger.error(f"Cannot get bruin circuit id using {json.dumps(msg)}. JSON malformed")
  ```
  END

* If message body doesn't have `circuit_id`:
  ```python
  logger.error(f'Cannot get bruin circuit id using {json.dumps(params)}. Need "circuit_id"')
  ```
  END

```python
logger.info(f"Getting Bruin circuit ID with filters: {json.dumps(params)}")
```

[get_circuit_id](../repositories/bruin_repository/get_circuit_id.md)

```python
logger.info(
            f"Bruin circuit ID published in event bus for request {json.dumps(msg)}. "
            f"Message published was {response}"
        )
```
