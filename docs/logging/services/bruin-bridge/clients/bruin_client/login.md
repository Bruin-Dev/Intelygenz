## Login

```python
self._logger.info("Logging into Bruin...")
```

Call Bruin Identity Server endpoint `POST /identity/connect/token` using authentication credentials.

* If no errors arise while calling the endpoint:
  ```python
  self._logger.info("Logged into Bruin!")
  ```
* Otherwise:
  ```python
  self._logger.error(f"An error occurred while trying to login to Bruin: {err}")
  ```