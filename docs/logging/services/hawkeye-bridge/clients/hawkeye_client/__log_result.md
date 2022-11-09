## Log result

* If status is 400
  ```python
  logger.error(f"Got error from Hawkeye -> {body}")
  ```
  
* If status is 401
  ```python
  logger.error(f"Authentication error -> {body}")
  ```

* If status is between 500 and 513
  ```python
  logger.error(f"Got {status} from Hawkeye")
  ```
