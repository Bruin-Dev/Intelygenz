# Get

```python
self.logger.debug(f"get(request={request})")
```

* Try
  _Get response from Bruin_
  * If response is not ok
    ```python
    self.logger.warning(f"get(request={request}) => response={response}")
    ```
    END
  
* If there's an error while connecting to Bruin API:
  ```python
  self.logger.error(f"get(request={request}) => ClientConnectionError: {e}")
  ```
  END

* Catch general exception:
  ```python
  self.logger.error(f"get(request={request}) => UnexpectedError: {e}")
  ```
  END