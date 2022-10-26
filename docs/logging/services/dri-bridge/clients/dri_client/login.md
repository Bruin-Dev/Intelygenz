# Log in to DRI API

```python
logger.info("Logging into DRI...")
```

Make a call to `POST /auth/login` using the set of credentials provided.

* If there's an error while connecting to DRI API:
  ```python
  logger.error("An error occurred while trying to login to DRI")
  logger.error(f"Error: {err}")
  ```
  END

```python
logger.info("Logged into DRI!")
```