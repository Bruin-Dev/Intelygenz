## Login

```python
logger.info("Logging into Hawkeye...")
```

Call Hawkeye endpoint `POST /login` using authentication credentials.

* If no errors arise while calling the endpoint:
  ```python
  logger.info("Logged into Hawkeye!")
  logger.info("Loading authentication cookie into the cookie jar...")
  logger.info("Loaded authentication cookie into the cookie jar!")
  ```
* Otherwise:

    [__log_result](__log_result.md)
