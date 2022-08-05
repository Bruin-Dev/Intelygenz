## Get links with edge info

* If there's no client authenticated against the VeloCloud host:
    ```python
    logger.error(f"Cannot find a client to connect to {velocloud_host}")
    ```

    [_start_relogin_job](_start_relogin_job.md)

    [__log_result](__log_result.md)

    END

```python
logger.info(f'Getting links with edge info from Velocloud host "{velocloud_host}"...')
```
  
Call VeloCloud API endpoint `POST /monitoring/getEnterpriseEdgeLinkStatus` with the set of desired parameters.

* If there's an error while connecting to VeloCloud API:
  
    [__log_result](__log_result.md)

    END

* If the status of the HTTP response is between `500` and `512` (both inclusive):

    [__log_result](__log_result.md)

    END

[__schedule_relogin_job_if_needed](__schedule_relogin_job_if_needed.md)

```python
logger.info(
    f"Got HTTP {response.status} from Velocloud after claiming links with edge info for host {velocloud_host}"
)
```

[__log_result](__log_result.md)