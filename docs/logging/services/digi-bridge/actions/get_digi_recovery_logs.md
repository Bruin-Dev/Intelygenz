## Subject: get.digi.recovery.logs

_Message arrives at subject_

* If message doesn't have `body`:
  ```python
  logger.error(f"Cannot get DiGi recovery logs client using {request_msg}. JSON malformed")
  ```
  END

```python
logger.info(f"Getting DiGi recovery logs")
```

[DiGiRepository::get_digi_recovery_logs](../repositories/digi_repository/get_digi_recovery_logs.md)

```python
logger.info(
    f"DiGi recovery logs retrieved and publishing results in event bus for request {request_msg}. "
    f"Message published was {response}"
)
```
