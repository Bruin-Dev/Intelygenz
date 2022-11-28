## Get DiGi recovery logs

```python
logger.info(f"Getting DiGi recovery logs with params {request_filters}")
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
