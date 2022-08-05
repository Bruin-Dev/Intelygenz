## Get edge links series

* If there's no client authenticated against the VeloCloud host:
    ```python
    logger.error(f"Cannot find a client to connect to {velocloud_host}")
    ```

    [_start_relogin_job](_start_relogin_job.md)

    [__log_result](__log_result.md)

    END

```python
logger.info(f'Trying to get edge links series for payload {payload} from Velocloud host "{velocloud_host}"...')
```
  
Call VeloCloud API endpoint `POST /metrics/getEdgeLinkSeries` with the set of desired parameters.

* If there's an error while connecting to VeloCloud API:
  
    [__log_result](__log_result.md)

    END

* If the status of the HTTP response is between `500` and `512` (both inclusive):

    [__log_result](__log_result.md)

    END

[__schedule_relogin_job_if_needed](__schedule_relogin_job_if_needed.md)

```python
logger.info(
    f"Got HTTP {response.status} from Velocloud after fetching edge link series for {payload}"
    f"and host {velocloud_host}"
)
```

[__log_result](__log_result.md)