## DiGi reboot

```python
logger.info(f"Rebooting DiGi device with params {request_filters}")
```

[check_if_token_is_created_and_valid](check_if_token_is_created_and_valid.md)

Make a call to `POST /DeviceManagement_API/rest/Recovery/RecoverDevice` with the specified query parameters.

* If an error took place:
  ```python
  logger.error(f"Got an error of {response_error_list}")
  ```
  END

* If DiGi aborted the request:
  ```python
  logger.error(f"DiGi reboot aborted with message returning: {response_abort_messages_list}")
  ```
  END

* If DiGi returned a response but the request couldn't succeed on their system:
  ```python
  logger.error(f"Got {response.status}. Response returned {response_json}")
  ```
  END
