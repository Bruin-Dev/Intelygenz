## DiGi reboot

```python
logger.info(f"Rebooting DiGi device with params {request_filters}")
```

* If the auth token has not been created yet:
  ```python
  error_token_msg = f"The token is not created yet"
  bad_token_msg = f"{error_token_msg}. Please try in a few seconds"
  logger.error(bad_token_msg)
  ```
  END

* If the existing auth token has expired:
  ```python
  error_token_msg = f"The token is not valid because it is expired"
  bad_token_msg = f"{error_token_msg}. Please try in a few seconds"
  logger.error(bad_token_msg)
  ```
  END

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
