## Login

```python
logger.info(f"Logging in to host {host}...")
```

Call VeloCloud API endpoint `POST /login/operatorLogin` with the set of desired parameters.

* If the status of the HTTP response is between `200` and `300` (both inclusive):
    ```python
    logger.info(f"Logged in to host {host} successfully")
    ```
* Otherwise:
    ```python
    logger.error(f"Got HTTP {response.status} while logging in to host {host}")
    ```

* If there was an exception:
    ```python
    logger.exception(e)
    ```