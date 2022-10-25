# Post

```python
self.logger.debug(f"post(request={request}")
```

* Try
  _Get response from Bruin_
  * If response is not ok
    ```python
    self.logger.warning(f"post(request={request}) => response={response}")
    ```
    END
  
* If there's an error while connecting to Bruin API:
  ```python
  self.logger.error(f"post(request={request}) => ClientConnectionError: {e}")
  ```
  END

* Catch general exception:
  ```python
  self.logger.error(f"post(request={request}) => UnexpectedError: {e}")
  ```
  END