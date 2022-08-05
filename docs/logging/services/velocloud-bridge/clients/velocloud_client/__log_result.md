## Log result

* If result status is `400`:
  ```python
  logger.error(f"Got error from Velocloud -> {body}")
  ```

* If result status is `401`:
  ```python
  logger.error(f"Authentication error -> {body}")
  ```

* If result status is between `500` and `512` (both inclusive):
  ```python
  logger.error(f"Got {status} from Velocloud")
  ```