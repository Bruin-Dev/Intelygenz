## Subject: digi.reboot

_Message arrives at subject_

* If message doesn't have `body`:
  ```python
  logger.error(f"Cannot reboot DiGi client using {request_msg}. JSON malformed")
  ```
  END

* If message body doesn't have `velo_serial`, `ticket` and `MAC` filters:
  ```python
  logger.error(f"Cannot reboot DiGi client using {request_msg}. JSON malformed")
  ```
  END

```python
logger.info(f"Attempting to reboot DiGi client with payload of: {request_filters}")
```

[DiGiRepository::reboot](../repositories/digi_repository/reboot.md)

```python
logger.info(
    f"DiGi reboot process completed and publishing results in event bus for request {request_msg}. "
    f"Message published was {response}"
)
```
