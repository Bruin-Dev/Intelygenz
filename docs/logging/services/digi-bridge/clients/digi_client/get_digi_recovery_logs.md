## Get DiGi recovery logs

```python
logger.info(f"Getting DiGi recovery logs with params {request_filters}")
```

[check_if_token_is_created_and_valid](check_if_token_is_created_and_valid.md)

Make a call to `GET /DeviceManagement_API/rest/Recovery/Logs` with the specified query parameters.

* If an error took place:
  ```python
  logger.error(f"Got an error of {return_response['body']}")
  ```
  END

* If DiGi returned a response but the request couldn't succeed on their system:
  ```python
  logger.error(f"Got {response.status}. Response returned {response_json}")
  ```
  END
