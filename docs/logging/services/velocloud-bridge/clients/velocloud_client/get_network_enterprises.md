## Get network enterprises

```python
logger.info(
    f"Getting network enterprise edges for host {velocloud_host} and enterprises {enterprise_ids}..."
)
```
  
Call VeloCloud API endpoint `POST /network/getNetworkEnterprises` with the set of desired parameters.

* If there's an error while connecting to VeloCloud API:
  
    [__log_result](__log_result.md)

    END

* If the status of the HTTP response is between `500` and `512` (both inclusive):

    [__log_result](__log_result.md)

    END

* If the status of the HTTP response is `400`:

    [__log_result](__log_result.md)

    END

* If the status of the HTTP response is any other:

    [__schedule_relogin_job_if_needed](__schedule_relogin_job_if_needed.md)

    ```python
    logger.info(
        f"Got HTTP {response.status} from Velocloud after getting enterprise ids: {enterprise_ids} "
        f"from host {velocloud_host}"
    )
    ```

    [__log_result](__log_result.md)