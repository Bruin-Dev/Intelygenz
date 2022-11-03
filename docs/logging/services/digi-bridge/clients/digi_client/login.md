## Login

```python
logger.info("Scheduled task: logging in digi api")
```

Call DiGi Identity Server endpoint `POST /Identity/rest/oauth/token` using authentication credentials.

* If no errors arise while calling the endpoint:
  ```python
  logger.info("Logged into DiGi!")
  ```
* Otherwise:
  ```python
  logger.error("An error occurred while trying to login to DiGi")
  logger.error(f"Error: {err}")
  ```
  