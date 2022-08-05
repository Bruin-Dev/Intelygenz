## Create headers by host

```python
logger.info(f"Logging in to host {host}...")
```

Make HTTP call to `POST /login/operatorLogin`.

* If response status for logging in to the VeloCloud host is ok:
  ```python
  logger.info(f"Logged in to host {host} successfully")
  ```
  
* If response status for logging in to the VeloCloud host is `302`:
  ```python
  logger.error(f"Got HTTP 302 while logging in to host {host}")
  ```