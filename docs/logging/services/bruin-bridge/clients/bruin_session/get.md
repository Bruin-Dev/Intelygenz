# Get

```python
logger.debug(f"get(request={request})")
```

* Try
  _Get response from Bruin_
  * If response is not ok
    ```python
    logger.warning(f"get(request={request}) => response={response}")
    ```
    END
  
* If there's an error while connecting to Bruin API:
  ```python
  logger.error(f"get(request={request}) => ClientConnectionError: {e}")
  ```
  END

* Catch general exception:
  ```python
  logger.error(f"get(request={request}) => UnexpectedError: {e}")
  ```
  END